import geopandas as gpd
from shapely.geometry import box


BRAZIL_BOUNDS = (-74.0, -34.0, -34.0, 6.0)


def filter_geometries_in_brazil_bounds(gdf):
    if "geometry" not in gdf.columns:
        return gdf.iloc[0:0].copy()

    bounds_geom = box(*BRAZIL_BOUNDS)
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


__all__ = ["BRAZIL_BOUNDS", "filter_geometries_in_brazil_bounds"]
