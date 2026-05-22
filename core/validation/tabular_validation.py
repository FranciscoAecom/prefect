import pandas as pd

from core.validation.schema_presence import validate_geometry, validate_schema_presence


def validate_tabular_schema(gdf, schema):
    errors = validate_schema_presence(gdf, schema)
    for column, rule in schema.columns.items():
        if column not in gdf.columns:
            continue

        errors.extend(validate_column(gdf[column], column, rule))

    return errors


def validate_column(series, column, rule):
    errors = []

    if not rule.nullable and series.isna().any():
        errors.append(f"Coluna {column} nao permite valores nulos.")

    if not matches_dtype(series, rule.dtype):
        errors.append(
            f"Coluna {column} tem tipo invalido: "
            f"esperado {rule.dtype}, encontrado {series.dtype}."
        )

    return errors


def matches_dtype(series, expected_dtype):
    expected = str(expected_dtype).strip().lower()

    if expected in {"string", "str", "text"}:
        return (
            pd.api.types.is_string_dtype(series)
            or pd.api.types.is_object_dtype(series)
        )

    if expected in {"number", "numeric"}:
        return pd.api.types.is_numeric_dtype(series)

    if expected in {"float", "double"}:
        return pd.api.types.is_float_dtype(series) or pd.api.types.is_numeric_dtype(series)

    if expected in {"integer", "int"}:
        return pd.api.types.is_integer_dtype(series)

    if expected in {"datetime", "date"}:
        return pd.api.types.is_datetime64_any_dtype(series)

    if expected in {"boolean", "bool"}:
        return pd.api.types.is_bool_dtype(series)

    return True
