from pathlib import Path

import geopandas as gpd
import pandas as pd

from core.ingest.dataset_resolver import resolve_input_dataset_paths
from core.ingest.normalization import normalize_status, normalize_theme_folder, stringify
from core.io.dataset import read_input_dataset
from core.prefect_support.variables import get_str_variable
from core.transforms.attribute_transforms import normalize_columns
from core.utils import log
from core.config.defaults import DEFAULT_MUNICIPALITIES_BASE_PATH
from settings import (
    INGEST_WORKBOOK_PATH,
    INGEST_SHEET_NAME,
)


MUNICIPALITIES_BASE_VARIABLE = "municipios_base_path"
MUNICIPALITY_CODE_COLUMNS = ("sdb_cd_mun", "cd_mun")
MUNICIPALITY_NAME_COLUMNS = ("sdb_nm_mun", "nm_mun")
MUNICIPALITY_UF_COLUMNS = ("sdb_sigla_uf", "sigla_uf", "sdb_cd_uf", "cd_uf")
OUTSIDE_TERRITORIAL_LIMIT_MESSAGE = "Fora do limite territorial brasileiro / zona costeira"
UF_CODE_TO_SIGLA = {
    "11": "RO",
    "12": "AC",
    "13": "AM",
    "14": "RR",
    "15": "PA",
    "16": "AP",
    "17": "TO",
    "21": "MA",
    "22": "PI",
    "23": "CE",
    "24": "RN",
    "25": "PB",
    "26": "PE",
    "27": "AL",
    "28": "SE",
    "29": "BA",
    "31": "MG",
    "32": "ES",
    "33": "RJ",
    "35": "SP",
    "41": "PR",
    "42": "SC",
    "43": "RS",
    "50": "MS",
    "51": "MT",
    "52": "GO",
    "53": "DF",
}


def enrich_with_municipality_intersection(gdf, municipalities_path=None):
    source_path = resolve_municipalities_base_path(municipalities_path)
    municipalities = load_municipalities_base(source_path)
    return assign_municipality_fields_by_intersection(gdf, municipalities)


def resolve_municipalities_base_path(municipalities_path=None):
    explicit_path = stringify(municipalities_path)
    if explicit_path:
        return explicit_path

    variable_path = stringify(get_str_variable(MUNICIPALITIES_BASE_VARIABLE, ""))
    if variable_path:
        return variable_path

    ingest_path = find_latest_municipalities_path_from_ingest()
    if ingest_path:
        return ingest_path

    default_path = stringify(DEFAULT_MUNICIPALITIES_BASE_PATH)
    if default_path and Path(default_path).exists():
        return default_path

    raise FileNotFoundError(
        "Base de municipios nao configurada. Defina a Prefect Variable "
        f"'{MUNICIPALITIES_BASE_VARIABLE}' apontando para o shapefile/GPKG de municipios."
    )


def find_latest_municipalities_path_from_ingest():
    if not Path(INGEST_WORKBOOK_PATH).exists():
        return None

    dataframe = pd.read_excel(INGEST_WORKBOOK_PATH, sheet_name=INGEST_SHEET_NAME)
    candidates = []
    for _, row in dataframe.iterrows():
        if normalize_theme_folder(row.get("theme_folder")) != "municipios":
            continue
        if normalize_status(row.get("status")) != "complete":
            continue
        path = stringify(row.get("path_shapefile_temp"))
        if path and Path(path).exists():
            candidates.append((row.get("date_stamp"), row.get("date"), path))

    if not candidates:
        return None

    candidates.sort(key=lambda item: (str(item[0]), str(item[1]), item[2]))
    return candidates[-1][2]


def load_municipalities_base(path_value):
    dataset_paths = resolve_input_dataset_paths(path_value)
    if not dataset_paths:
        raise FileNotFoundError(f"Nenhuma base de municipios encontrada em: {path_value}")

    municipalities = read_input_dataset(dataset_paths[0])
    municipalities = normalize_columns(municipalities)
    validate_municipality_columns(municipalities)
    return municipalities


def validate_municipality_columns(municipalities):
    missing = []
    for label, candidates in {
        "codigo do municipio": MUNICIPALITY_CODE_COLUMNS,
        "nome do municipio": MUNICIPALITY_NAME_COLUMNS,
        "UF": MUNICIPALITY_UF_COLUMNS,
    }.items():
        if not first_existing_column(municipalities, candidates):
            missing.append(label)

    if missing:
        raise ValueError(
            "Base de municipios sem coluna(s) esperada(s): " + ", ".join(missing)
        )

    if "geometry" not in municipalities.columns:
        raise ValueError("Base de municipios sem coluna geometry.")


def assign_municipality_fields_by_intersection(gdf, municipalities):
    if "geometry" not in gdf.columns:
        raise ValueError("Base autos_infracao sem coluna geometry para intersecao municipal.")

    code_column = first_existing_column(municipalities, MUNICIPALITY_CODE_COLUMNS)
    name_column = first_existing_column(municipalities, MUNICIPALITY_NAME_COLUMNS)
    uf_column = first_existing_column(municipalities, MUNICIPALITY_UF_COLUMNS)

    if municipalities.crs != gdf.crs:
        municipalities = municipalities.to_crs(gdf.crs)

    left = gdf.copy()
    left["__autos_infracao_index"] = left.index
    right = municipalities[[code_column, name_column, uf_column, "geometry"]].rename(
        columns={
            code_column: "__mun_cod",
            name_column: "__mun_nome",
            uf_column: "__mun_uf",
        }
    )

    joined = gpd.sjoin(
        left[["__autos_infracao_index", "geometry"]],
        right,
        how="left",
        predicate="intersects",
    )
    joined = joined.dropna(subset=["index_right"])
    joined = joined.drop_duplicates(subset=["__autos_infracao_index"], keep="first")
    joined = joined.set_index("__autos_infracao_index")

    enriched = gdf.copy()
    enriched["acm_cod_munici"] = joined["__mun_cod"].reindex(enriched.index)
    enriched["acm_municipio"] = joined["__mun_nome"].reindex(enriched.index)
    enriched["acm_uf"] = normalize_uf_values(joined["__mun_uf"]).reindex(enriched.index)
    enriched = fill_missing_municipality_intersection(enriched)
    enriched = fill_missing_uf_from_source(enriched)

    matched = int(enriched["acm_cod_munici"].notna().sum())
    log(
        "Intersecao municipal autos_infracao: "
        f"{matched} de {len(enriched)} feicao(oes) receberam municipio/UF."
    )
    return enriched


def fill_missing_municipality_intersection(gdf):
    missing_mask = gdf["acm_cod_munici"].isna()
    if not missing_mask.any():
        return gdf

    for column in ("acm_cod_munici", "acm_municipio", "acm_uf"):
        gdf[column] = gdf[column].astype("object")
        gdf.loc[missing_mask, column] = OUTSIDE_TERRITORIAL_LIMIT_MESSAGE

    return gdf


def fill_missing_uf_from_source(gdf):
    if "acm_uf" not in gdf.columns or "sdb_uf" not in gdf.columns:
        return gdf

    missing_mask = gdf["acm_uf"].isna() & gdf["sdb_uf"].notna()
    if bool(missing_mask.any()):
        gdf.loc[missing_mask, "acm_uf"] = normalize_uf_values(
            gdf.loc[missing_mask, "sdb_uf"]
        )
    return gdf


def first_existing_column(dataframe, candidates):
    for column in candidates:
        if column in dataframe.columns:
            return column
    return None


def normalize_uf_values(values):
    series = values.astype("string").str.strip()
    code_series = series.str.replace(r"\.0$", "", regex=True).str.zfill(2)
    mapped = code_series.map(UF_CODE_TO_SIGLA)
    return mapped.fillna(series.str.upper())


__all__ = [
    "MUNICIPALITIES_BASE_VARIABLE",
    "OUTSIDE_TERRITORIAL_LIMIT_MESSAGE",
    "assign_municipality_fields_by_intersection",
    "enrich_with_municipality_intersection",
    "fill_missing_uf_from_source",
    "fill_missing_municipality_intersection",
    "find_latest_municipalities_path_from_ingest",
    "load_municipalities_base",
    "normalize_uf_values",
    "resolve_municipalities_base_path",
]
