from __future__ import annotations

import shutil
from pathlib import Path

from core.ingest.dataset_resolver import SUPPORTED_DATASET_SUFFIXES
from core.ingest.normalization import stringify
from core.utils import log


SHAPEFILE_SIDECAR_SUFFIXES = {
    ".shp",
    ".shx",
    ".dbf",
    ".prj",
    ".cpg",
    ".qix",
    ".sbn",
    ".sbx",
    ".xml",
    ".cst",
}


def ensure_bronze_dataset(record):
    bronze_dir_value = stringify(getattr(record, "bronze_dir", ""))
    if not bronze_dir_value:
        return None

    bronze_dir = Path(bronze_dir_value)
    bronze_dir.mkdir(parents=True, exist_ok=True)

    existing_dataset = find_first_geographic_dataset(bronze_dir)
    if existing_dataset:
        return existing_dataset

    source = resolve_bronze_source(record)
    if not source or not source.exists():
        log(
            "Bronze nao materializado: arquivo/pasta de origem nao encontrado "
            f"para copia do dado bruto: {source}"
        )
        return None

    if _same_path_or_parent(source, bronze_dir):
        return find_first_geographic_dataset(bronze_dir)

    copied_files = copy_raw_source_to_bronze(source, bronze_dir)
    if copied_files:
        log(f"Dado bruto copiado para bronze: {bronze_dir}")
    else:
        log(f"Nenhum arquivo bruto elegivel encontrado para copiar ao bronze: {source}")
    return find_first_geographic_dataset(bronze_dir)


def resolve_bronze_source(record):
    source_path = Path(stringify(getattr(record, "source_path", "")))
    if source_path.exists():
        return source_path

    input_path = Path(stringify(getattr(record, "input_path", "")))
    if input_path.exists():
        return input_path

    return source_path if stringify(getattr(record, "source_path", "")) else input_path


def copy_raw_source_to_bronze(source, bronze_dir):
    source = Path(source)
    bronze_dir = Path(bronze_dir)
    copied_files = []

    if source.is_dir():
        for candidate in source.rglob("*"):
            if not candidate.is_file() or should_skip_metadata_xml(candidate):
                continue
            destination = bronze_dir / candidate.relative_to(source)
            copy_file(candidate, destination)
            copied_files.append(destination)
        return copied_files

    for candidate in related_dataset_files(source):
        if should_skip_metadata_xml(candidate):
            continue
        destination = bronze_dir / candidate.name
        copy_file(candidate, destination)
        copied_files.append(destination)
    return copied_files


def related_dataset_files(dataset_path):
    dataset_path = Path(dataset_path)
    if dataset_path.suffix.lower() == ".shp":
        return sorted(
            candidate
            for candidate in dataset_path.parent.iterdir()
            if candidate.is_file()
            and candidate.stem == dataset_path.stem
            and candidate.suffix.lower() in SHAPEFILE_SIDECAR_SUFFIXES
        )
    return [dataset_path]


def copy_file(source, destination):
    destination.parent.mkdir(parents=True, exist_ok=True)
    if source.resolve() == destination.resolve():
        return
    shutil.copy2(source, destination)


def should_skip_metadata_xml(path):
    path = Path(path)
    return path.suffix.lower() == ".xml" and path.name.lower().startswith("md_")


def find_first_geographic_dataset(directory):
    directory = Path(directory)
    if not directory.exists():
        return None
    for suffix in (".gpkg", ".shp", ".tif", ".tiff"):
        matches = sorted(
            candidate
            for candidate in directory.rglob(f"*{suffix}")
            if candidate.is_file()
            and candidate.suffix.lower() in SUPPORTED_DATASET_SUFFIXES
        )
        if matches:
            return matches[0]
    return None


def _same_path_or_parent(source, target_dir):
    try:
        source_resolved = source.resolve()
        target_resolved = target_dir.resolve()
    except OSError:
        return False
    return source_resolved == target_resolved or target_resolved in source_resolved.parents


__all__ = ["ensure_bronze_dataset", "find_first_geographic_dataset"]
