DATA_SUFFIXES = {".gpkg", ".rst", ".tif"}
SPATIAL_PREFIXES = {"pnt", "pol", "lin", "rst"}


class MultiplePublishItemsError(RuntimeError):
    pass


__all__ = ["DATA_SUFFIXES", "MultiplePublishItemsError", "SPATIAL_PREFIXES"]
