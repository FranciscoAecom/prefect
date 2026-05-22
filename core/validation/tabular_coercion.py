import pandas as pd

from core.utils import log
from core.validation.schema_presence import validate_schema_presence
from core.validation.tabular_validation import (
    matches_dtype,
    validate_column,
)


def normalize_tabular_schema(gdf, schema):
    errors = validate_schema_presence(gdf, schema)
    for column, rule in schema.columns.items():
        if column not in gdf.columns:
            continue

        gdf, column_errors = normalize_column(gdf, column, rule)
        errors.extend(column_errors)

    return gdf, errors


def normalize_column(gdf, column, rule):
    source_series = gdf[column]
    normalized_series = source_series

    if not matches_dtype(source_series, rule.dtype):
        normalized_series = coerce_series(source_series, rule.dtype)

        if matches_dtype(normalized_series, rule.dtype):
            changed_nulls = new_null_count(source_series, normalized_series)
            if changed_nulls and not rule.nullable:
                return gdf, [
                    f"Coluna {column} nao pode ser convertida para {rule.dtype} "
                    f"sem gerar {changed_nulls} valor(es) nulo(s)."
                ]

            gdf[column] = normalized_series
            log(
                "Schema tabular: coluna "
                f"{column} convertida de {source_series.dtype} para {gdf[column].dtype}."
            )

    return gdf, validate_column(gdf[column], column, rule)


def coerce_series(series, expected_dtype):
    expected = str(expected_dtype).strip().lower()

    if expected in {"string", "str", "text"}:
        return series.astype("string")

    if expected in {"number", "numeric", "float", "double"}:
        return pd.to_numeric(series, errors="coerce")

    if expected in {"integer", "int"}:
        numeric = pd.to_numeric(series, errors="coerce")
        non_null = numeric.dropna()
        if ((non_null % 1) == 0).all():
            return numeric.astype("Int64")
        return numeric

    if expected in {"datetime", "date"}:
        return pd.to_datetime(series, errors="coerce")

    if expected in {"boolean", "bool"}:
        return coerce_bool_series(series)

    return series


def coerce_bool_series(series):
    if pd.api.types.is_numeric_dtype(series):
        mapped = series.map({0: False, 1: True})
        return mapped.astype("boolean") if mapped.notna().all() else mapped

    normalized = series.astype("string").str.strip().str.casefold()
    mapped = normalized.map(
        {
            "true": True,
            "false": False,
            "1": True,
            "0": False,
            "sim": True,
            "nao": False,
            "yes": True,
            "no": False,
        }
    )
    return mapped.astype("boolean") if mapped.notna().all() else mapped


def new_null_count(source_series, candidate_series):
    source_nulls = source_series.isna()
    candidate_nulls = candidate_series.isna()
    return int((~source_nulls & candidate_nulls).sum())
