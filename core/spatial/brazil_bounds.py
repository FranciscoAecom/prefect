from functools import lru_cache
from pathlib import Path

import geopandas as gpd
import pandas as pd
from shapely.geometry import Point, box
from shapely.ops import unary_union

from core.config.defaults import DEFAULT_BRAZIL_BBOX_PATH

BRAZIL_CENTROID_LONGITUDE_FIELD = "acm_long_centroide_brasil"
BRAZIL_CENTROID_LATITUDE_FIELD = "acm_lat_centroide_brasil"

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


def relocate_geometries_outside_brazil_bounds_to_centroid(gdf):
    if "geometry" not in gdf.columns:
        return gdf.copy()

    output = gdf.copy()
    bounds_geom = get_brazil_bounds_geometry(output.crs)
    geometry = output.geometry
    valid_mask = geometry.notna() & (~geometry.is_empty)
    outside_mask = valid_mask & (~geometry.intersects(bounds_geom))
    if not outside_mask.any():
        return output

    centroid = brazil_bounds_centroid(output.crs)
    if BRAZIL_CENTROID_LONGITUDE_FIELD not in output.columns:
        output[BRAZIL_CENTROID_LONGITUDE_FIELD] = pd.NA
    if BRAZIL_CENTROID_LATITUDE_FIELD not in output.columns:
        output[BRAZIL_CENTROID_LATITUDE_FIELD] = pd.NA

    output.loc[outside_mask, "geometry"] = [
        Point(centroid.x, centroid.y)
        for _ in range(int(outside_mask.sum()))
    ]
    output.loc[outside_mask, BRAZIL_CENTROID_LONGITUDE_FIELD] = round(centroid.x, 6)
    output.loc[outside_mask, BRAZIL_CENTROID_LATITUDE_FIELD] = round(centroid.y, 6)
    if "acm_long" in output.columns:
        output.loc[outside_mask, "acm_long"] = round(centroid.x, 6)
    if "acm_lat" in output.columns:
        output.loc[outside_mask, "acm_lat"] = round(centroid.y, 6)
    return gpd.GeoDataFrame(output, geometry="geometry", crs=gdf.crs)


def brazil_bounds_centroid(target_crs=None):
    bounds_geom = get_brazil_bounds_geometry(target_crs)
    centroid = bounds_geom.centroid
    if bounds_geom.covers(centroid):
        return centroid
    return bounds_geom.representative_point()


@lru_cache(maxsize=4)
def get_brazil_bounds_geometry(target_crs=None):
    source_path = Path(DEFAULT_BRAZIL_BBOX_PATH) if DEFAULT_BRAZIL_BBOX_PATH else None
    if source_path and source_path.exists():
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
    "BRAZIL_CENTROID_LATITUDE_FIELD",
    "BRAZIL_CENTROID_LONGITUDE_FIELD",
    "brazil_bounds_centroid",
    "filter_geometries_in_brazil_bounds",
    "get_brazil_bounds_geometry",
    "relocate_geometries_outside_brazil_bounds_to_centroid",
]
