import unittest
from unittest.mock import patch

import geopandas as gpd
from shapely.geometry import Point

from core.spatial.brazil_bounds import (
    BRAZIL_BOUNDS,
    filter_geometries_in_brazil_bounds,
    get_brazil_bounds_geometry,
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


if __name__ == "__main__":
    unittest.main()
