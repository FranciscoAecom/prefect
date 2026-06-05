DATA_SUFFIXES = {".gpkg"}
SPATIAL_PREFIXES = {"pnt", "pol", "lin"}


class MultiplePublishItemsError(RuntimeError):
    pass


__all__ = ["DATA_SUFFIXES", "MultiplePublishItemsError", "SPATIAL_PREFIXES"]
