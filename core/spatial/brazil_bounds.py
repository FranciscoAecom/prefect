from functools import lru_cache
from pathlib import Path

import geopandas as gpd
from shapely.geometry import box
from shapely.ops import unary_union

from settings import DEFAULT_BRAZIL_BBOX_PATH

BRAZIL_BOUNDS = (
    -73.99044999999995,
    -37.245154277004936,
    -25.290947335149315,
    8.757636788451368,
)


def filter_geometries_in_brazil_bounds(gdf):
    if "geometry" not in gdf.columns:
        return gdf.iloc[0:0].copy()

    bounds_geom = get_brazil_bounds_geometry(gdf.crs)
    geometry = gdf.geometry
    valid_mask = geometry.notna() & (~geometry.is_empty)
    if not valid_mask.any():
        return gpd.GeoDataFrame(gdf.iloc[0:0].copy(), geometry="geometry", crs=gdf.crs)

    within_bounds_mask = valid_mask & geometry.intersects(bounds_geom)
    return gpd.GeoDataFrame(
        gdf.loc[within_bounds_mask].copy(),
        geometry="geometry",
        crs=gdf.crs,
    )


@lru_cache(maxsize=4)
def get_brazil_bounds_geometry(target_crs=None):
    source_path = Path(DEFAULT_BRAZIL_BBOX_PATH)
    if source_path.exists():
        bounds_gdf = gpd.read_file(source_path)
        if target_crs and bounds_gdf.crs and bounds_gdf.crs != target_crs:
            bounds_gdf = bounds_gdf.to_crs(target_crs)
        geometries = [
            geometry
            for geometry in bounds_gdf.geometry
            if geometry is not None and not geometry.is_empty
        ]
        if geometries:
            return unary_union(geometries)

    return box(*BRAZIL_BOUNDS)


__all__ = [
    "BRAZIL_BOUNDS",
    "filter_geometries_in_brazil_bounds",
    "get_brazil_bounds_geometry",
]
