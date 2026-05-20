import unittest

import geopandas as gpd
from shapely.geometry import Point

from core.spatial.brazil_bounds import filter_geometries_in_brazil_bounds


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


if __name__ == "__main__":
    unittest.main()
