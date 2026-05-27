import unittest
from unittest.mock import patch

import geopandas as gpd
import pandas as pd
from shapely.geometry import Point

from core.spatial.brazil_bounds import (
    BRAZIL_BOUNDS,
    BRAZIL_CENTROID_LATITUDE_FIELD,
    BRAZIL_CENTROID_LONGITUDE_FIELD,
    brazil_bounds_centroid,
    filter_geometries_in_brazil_bounds,
    get_brazil_bounds_geometry,
    relocate_geometries_outside_brazil_bounds_to_centroid,
)


class BrazilBoundsTests(unittest.TestCase):
    def test_filters_geometries_inside_brazil_bbox(self):
        gdf = gpd.GeoDataFrame(
            {
                "name": ["acre", "outside"],
                "geometry": [Point(-70.0, -9.0), Point(0.0, 50.0)],
            },
            geometry="geometry",
            crs="EPSG:4326",
        )

        result = filter_geometries_in_brazil_bounds(gdf)

        self.assertEqual(result["name"].tolist(), ["acre"])
        self.assertEqual(result.crs, gdf.crs)

    def test_uses_standard_brazil_bbox_extent_as_fallback(self):
        get_brazil_bounds_geometry.cache_clear()
        try:
            with patch("core.spatial.brazil_bounds.DEFAULT_BRAZIL_BBOX_PATH", "inexistente.shp"):
                bounds = get_brazil_bounds_geometry("EPSG:4326").bounds
        finally:
            get_brazil_bounds_geometry.cache_clear()

        self.assertEqual(bounds, BRAZIL_BOUNDS)

    def test_relocates_outside_geometries_to_single_brazil_centroid(self):
        gdf = gpd.GeoDataFrame(
            {
                "name": ["acre", "outside"],
                "acm_long": [-70.0, 0.0],
                "acm_lat": [-9.0, 50.0],
                "geometry": [Point(-70.0, -9.0), Point(0.0, 50.0)],
            },
            geometry="geometry",
            crs="EPSG:4326",
        )

        result = relocate_geometries_outside_brazil_bounds_to_centroid(gdf)
        centroid = brazil_bounds_centroid("EPSG:4326")

        self.assertEqual(result.loc[0, "geometry"], Point(-70.0, -9.0))
        self.assertEqual(result.loc[1, "geometry"], Point(centroid.x, centroid.y))
        self.assertEqual(result.loc[1, "acm_long"], round(centroid.x, 6))
        self.assertEqual(result.loc[1, "acm_lat"], round(centroid.y, 6))
        self.assertTrue(pd.isna(result.loc[0, BRAZIL_CENTROID_LONGITUDE_FIELD]))
        self.assertTrue(pd.isna(result.loc[0, BRAZIL_CENTROID_LATITUDE_FIELD]))
        self.assertEqual(
            result.loc[1, BRAZIL_CENTROID_LONGITUDE_FIELD],
            round(centroid.x, 6),
        )
        self.assertEqual(
            result.loc[1, BRAZIL_CENTROID_LATITUDE_FIELD],
            round(centroid.y, 6),
        )


if __name__ == "__main__":
    unittest.main()
