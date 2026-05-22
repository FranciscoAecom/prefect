import geopandas as gpd


def validate_schema_presence(gdf, schema):
    errors = []

    if schema.require_geometry:
        errors.extend(validate_geometry(gdf))

    missing_columns = required_missing_columns(gdf, schema)
    if missing_columns:
        errors.append(
            "Colunas obrigatorias ausentes: "
            f"{', '.join(missing_columns)}."
        )

    extra_columns = unexpected_columns(gdf, schema)
    if extra_columns:
        errors.append(
            "Colunas nao previstas no schema: "
            f"{', '.join(extra_columns)}."
        )

    return errors


def required_missing_columns(gdf, schema):
    return sorted(
        column
        for column, rule in schema.columns.items()
        if rule.required and column not in gdf.columns
    )


def unexpected_columns(gdf, schema):
    if schema.allow_extra_columns:
        return []
    expected_columns = set(schema.columns) | {"geometry"}
    return sorted(set(gdf.columns) - expected_columns)


def validate_geometry(gdf):
    if not isinstance(gdf, gpd.GeoDataFrame):
        return ["Entrada nao e um GeoDataFrame."]
    if "geometry" not in gdf.columns:
        return ["Coluna obrigatoria ausente: geometry."]
    if gdf.geometry.name != "geometry":
        return ["Coluna geometry nao esta configurada como geometria ativa."]
    return []


__all__ = [
    "required_missing_columns",
    "unexpected_columns",
    "validate_geometry",
    "validate_schema_presence",
]
