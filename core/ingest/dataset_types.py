from dataclasses import dataclass
from pathlib import Path

from core.ingest.normalization import stringify

DATASET_KIND_VECTOR = "vector"
DATASET_KIND_RASTER = "raster"


@dataclass(frozen=True)
class DatasetType:
    kind: str
    suffixes: frozenset[str]


DATASET_TYPES = (
    DatasetType(DATASET_KIND_VECTOR, frozenset({".shp", ".gpkg"})),
    DatasetType(DATASET_KIND_RASTER, frozenset({".tif", ".tiff"})),
)

VECTOR_DATASET_SUFFIXES = frozenset(
    suffix for dataset_type in DATASET_TYPES
    if dataset_type.kind == DATASET_KIND_VECTOR
    for suffix in dataset_type.suffixes
)
RASTER_DATASET_SUFFIXES = frozenset(
    suffix for dataset_type in DATASET_TYPES
    if dataset_type.kind == DATASET_KIND_RASTER
    for suffix in dataset_type.suffixes
)
SUPPORTED_DATASET_SUFFIXES = frozenset(
    suffix for dataset_type in DATASET_TYPES for suffix in dataset_type.suffixes
)


def dataset_kind_for_path(path_value):
    suffix = Path(stringify(path_value)).suffix.lower()
    for dataset_type in DATASET_TYPES:
        if suffix in dataset_type.suffixes:
            return dataset_type.kind
    return DATASET_KIND_VECTOR


def is_raster_dataset(path_value):
    return dataset_kind_for_path(path_value) == DATASET_KIND_RASTER


def is_vector_dataset(path_value):
    return dataset_kind_for_path(path_value) == DATASET_KIND_VECTOR


__all__ = [
    "DATASET_KIND_RASTER",
    "DATASET_KIND_VECTOR",
    "DATASET_TYPES",
    "DatasetType",
    "RASTER_DATASET_SUFFIXES",
    "SUPPORTED_DATASET_SUFFIXES",
    "VECTOR_DATASET_SUFFIXES",
    "dataset_kind_for_path",
    "is_raster_dataset",
    "is_vector_dataset",
]
