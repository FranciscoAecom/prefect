import os
import re
import sqlite3
import warnings
from contextlib import contextmanager
from pathlib import Path
from time import perf_counter, sleep, time

import pandas as pd
import pyogrio

from core.utils import log
from settings import USE_ARROW_IO


SUPPORTED_INPUT_SUFFIXES = {".shp", ".gpkg"}
OUTPUT_LOCK_STALE_SECONDS = 6 * 60 * 60
OUTPUT_LOCK_WAIT_SECONDS = 30 * 60


def _read_dataframe_with_fallback(path, layer=None):
    read_kwargs = {"layer": layer}
    path_obj = Path(path)
    is_shapefile = path_obj.suffix.lower() == ".shp"

    if is_shapefile and not path_obj.with_suffix(".cpg").exists():
        read_kwargs["encoding"] = "UTF-8"

    if USE_ARROW_IO and is_shapefile:
        log(
            "Leitura Arrow desabilitada para shapefile; usando leitura padrao do pyogrio "
            "com encoding declarado no .cpg ou UTF-8 quando o .cpg estiver ausente."
        )
    elif USE_ARROW_IO:
        try:
            return pyogrio.read_dataframe(path, use_arrow=True, **read_kwargs)
        except ImportError as exc:
            log(
                "Leitura Arrow indisponivel no ambiente atual; "
                f"voltando para a leitura padrao do pyogrio. Detalhe: {exc}"
            )
        except RuntimeError as exc:
            log(
                "Leitura Arrow nao pode ser utilizada neste ambiente; "
                f"voltando para a leitura padrao do pyogrio. Detalhe: {exc}"
            )
        except TypeError as exc:
            log(
                "A versao atual do pyogrio nao aceita use_arrow=True; "
                f"voltando para a leitura padrao. Detalhe: {exc}"
            )

    return pyogrio.read_dataframe(path, **read_kwargs)


def _select_input_layer(path):
    path_obj = Path(path)
    if path_obj.suffix.lower() != ".gpkg":
        return None

    layers = pyogrio.list_layers(path)
    if layers is None or len(layers) == 0:
        return None

    first = layers[0]
    if isinstance(first, (list, tuple)):
        return first[0]
    if hasattr(first, "__len__") and not isinstance(first, (str, bytes)):
        return first[0]
    return str(first)


def _log_captured_warnings(captured_warnings, path):
    seen_messages = set()

    for warning in captured_warnings:
        message = str(warning.message)
        if message in seen_messages:
            continue
        seen_messages.add(message)

        if "invalid winding order" in message.lower():
            log(
                f"Aviso de geometria na leitura de {path}: "
                "aneis de poligono com orientacao invalida foram autocorrigidos."
            )
        else:
            log(f"Aviso na leitura de {path}: {message}")


def inspect_input_attributes(path):
    layer = _select_input_layer(path)
    started = perf_counter()
    with warnings.catch_warnings(record=True) as captured_warnings:
        warnings.simplefilter("always")
        info = pyogrio.read_info(path, layer=layer)
    _log_captured_warnings(captured_warnings, path)
    log(f"Leitura de metadados concluida em {perf_counter() - started:.2f}s: {path}")

    fields = info.get("fields")
    if fields is None:
        return []
    return list(fields)


def read_input_dataset(path):
    layer = _select_input_layer(path)
    log(f"Iniciando leitura do arquivo de entrada: {path}")
    started = perf_counter()
    with warnings.catch_warnings(record=True) as captured_warnings:
        warnings.simplefilter("always")
        gdf = _read_dataframe_with_fallback(path, layer=layer)
    _log_captured_warnings(captured_warnings, path)
    log(f"Leitura do arquivo concluida em {perf_counter() - started:.2f}s: {path}")
    return gdf


def _remove_existing_gpkg_artifacts(output):
    for candidate in [
        output,
        output.with_name(f"{output.name}-wal"),
        output.with_name(f"{output.name}-shm"),
    ]:
        if candidate.exists():
            os.remove(candidate)


@contextmanager
def _output_file_lock(output):
    lock_path = output.with_name(f"{output.name}.lock")
    started = time()

    while True:
        try:
            fd = os.open(lock_path, os.O_CREAT | os.O_EXCL | os.O_WRONLY)
            with os.fdopen(fd, "w", encoding="utf-8") as lock_file:
                lock_file.write(str(os.getpid()))
            break
        except FileExistsError:
            try:
                lock_age = time() - lock_path.stat().st_mtime
                if lock_age > OUTPUT_LOCK_STALE_SECONDS:
                    lock_path.unlink()
                    continue
            except FileNotFoundError:
                continue

            if time() - started > OUTPUT_LOCK_WAIT_SECONDS:
                raise TimeoutError(
                    f"Tempo excedido aguardando liberacao da escrita: {output}"
                )
            sleep(1)

    try:
        yield
    finally:
        try:
            lock_path.unlink()
        except FileNotFoundError:
            pass


def _quoted_identifier(identifier):
    return '"' + str(identifier).replace('"', '""') + '"'


def _date_only_datetime_columns(gdf):
    date_columns = []
    for column in gdf.columns:
        if column == getattr(gdf, "geometry", None).name:
            continue
        series = gdf[column]
        if not pd.api.types.is_datetime64_any_dtype(series):
            continue

        parsed = pd.to_datetime(series, errors="coerce")
        non_null = parsed.dropna()
        if non_null.empty or bool(non_null.eq(non_null.dt.normalize()).all()):
            date_columns.append(column)
    return date_columns


def _promote_gpkg_datetime_columns_to_date(output, layer_name, date_columns):
    if not date_columns:
        return

    connection = sqlite3.connect(output)
    try:
        table_sql_row = connection.execute(
            """
            SELECT sql
            FROM sqlite_master
            WHERE type = 'table' AND name = ?
            """,
            (layer_name,),
        ).fetchone()
        if not table_sql_row or not table_sql_row[0]:
            return

        updated_sql = table_sql_row[0]
        for column in date_columns:
            quoted_column = re.escape(_quoted_identifier(column))
            updated_sql = re.sub(
                rf"({quoted_column}\s+)DATETIME\b",
                r"\1DATE",
                updated_sql,
                flags=re.IGNORECASE,
            )

        if updated_sql == table_sql_row[0]:
            return

        connection.execute("PRAGMA writable_schema=ON")
        try:
            connection.execute(
                """
                UPDATE sqlite_master
                SET sql = ?
                WHERE type = 'table' AND name = ?
                """,
                (updated_sql, layer_name),
            )
            schema_version = connection.execute("PRAGMA schema_version").fetchone()[0]
            connection.execute(f"PRAGMA schema_version = {int(schema_version) + 1}")
        finally:
            connection.execute("PRAGMA writable_schema=OFF")
        connection.commit()
    finally:
        connection.close()


def write_output_gpkg(
    gdf,
    output_path,
    layer=None,
    append=False,
    overwrite_existing=False,
):
    output = Path(output_path)
    output.parent.mkdir(parents=True, exist_ok=True)
    layer_name = layer or output.stem
    date_only_columns = _date_only_datetime_columns(gdf)
    started = perf_counter()
    with _output_file_lock(output):
        if overwrite_existing and not append:
            _remove_existing_gpkg_artifacts(output)
        with warnings.catch_warnings():
            warnings.filterwarnings(
                "ignore",
                message=r".*Only 0 or 1 should be passed for a OFSTBoolean subtype.*",
                category=RuntimeWarning,
            )
            pyogrio.write_dataframe(
                gdf,
                output,
                layer=layer_name,
                driver="GPKG",
                append=append,
            )
            _promote_gpkg_datetime_columns_to_date(
                output,
                layer_name,
                date_only_columns,
            )
        log(
            f"Escrita do arquivo concluida em {perf_counter() - started:.2f}s: "
            f"{output}"
        )
    return str(output)
