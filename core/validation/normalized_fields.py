SOURCE_FIELD_PREFIX = "sdb_"
NORMALIZED_FIELD_PREFIX = "acm_"


def is_source_column(column):
    return str(column).startswith(SOURCE_FIELD_PREFIX)


def is_normalized_column(column):
    return str(column).startswith(NORMALIZED_FIELD_PREFIX)


def normalized_column_name(column):
    column_text = str(column)
    if is_source_column(column_text):
        return f"{NORMALIZED_FIELD_PREFIX}{column_text[len(SOURCE_FIELD_PREFIX):]}"
    if is_normalized_column(column_text):
        return column_text
    return f"{NORMALIZED_FIELD_PREFIX}{column_text}"


def target_column_name(column):
    return normalized_column_name(column)


def series_has_normalized_changes(source_series, normalized_series):
    same_mask = source_series.eq(normalized_series)
    same_mask = same_mask | (source_series.isna() & normalized_series.isna())
    same_mask = same_mask.fillna(False)
    return not bool(same_mask.all())


def apply_normalized_column_if_changed(
    gdf,
    source_column,
    normalized_series,
    target_column=None,
):
    target_column = target_column or normalized_column_name(source_column)
    source_series = gdf[source_column]
    if series_has_normalized_changes(source_series, normalized_series):
        gdf[target_column] = normalized_series
    elif target_column in gdf.columns:
        gdf = gdf.drop(columns=[target_column])
    return gdf


__all__ = [
    "NORMALIZED_FIELD_PREFIX",
    "SOURCE_FIELD_PREFIX",
    "apply_normalized_column_if_changed",
    "is_normalized_column",
    "is_source_column",
    "normalized_column_name",
    "series_has_normalized_changes",
    "target_column_name",
]
