from pandas.api.types import is_object_dtype, is_string_dtype


def normalize_columns(gdf):
    new = []
    for c in gdf.columns:
        if c == "geometry":
            new.append(c)
            continue

        name = c.lower().replace(" ", "_")
        if not name.startswith("sdb_"):
            name = "sdb_" + name

        new.append(name)

    gdf.columns = new
    return gdf


def is_normalized_columns(gdf):
    return all(c == "geometry" or c.lower().startswith("sdb_") for c in gdf.columns)


def clean_whitespace(gdf):
    for c in gdf.columns:
        if is_object_dtype(gdf[c]) or is_string_dtype(gdf[c]):
            gdf[c] = gdf[c].map(_clean_text_value)
    return gdf


def _clean_text_value(value):
    if not isinstance(value, str):
        return value
    return " ".join(value.split())


def add_sequential_id(gdf, start=1):
    from settings import ID_FIELD
    gdf[ID_FIELD] = range(start, start + len(gdf))
    return gdf
