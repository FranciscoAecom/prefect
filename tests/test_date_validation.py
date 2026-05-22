import unittest

import geopandas as gpd
import pandas as pd
from shapely.geometry import Point

from core.date import validate_date_fields


class DateValidationTests(unittest.TestCase):
    def test_keeps_source_column_when_already_date(self):
        gdf = gpd.GeoDataFrame(
            {
                "sdb_data": pd.to_datetime(["2026-05-14"]),
                "geometry": [Point(0, 0)],
            },
            geometry="geometry",
            crs="EPSG:4326",
        )

        result = validate_date_fields(gdf, "sdb_data")

        self.assertIn("sdb_data", result.columns)
        self.assertNotIn("acm_data", result.columns)
        self.assertEqual(result.loc[0, "sdb_data"], pd.Timestamp("2026-05-14"))

    def test_creates_acm_column_when_source_date_is_text(self):
        gdf = gpd.GeoDataFrame(
            {
                "sdb_data": ["14/05/2026"],
                "geometry": [Point(0, 0)],
            },
            geometry="geometry",
            crs="EPSG:4326",
        )

        result = validate_date_fields(gdf, "sdb_data")

        self.assertEqual(result.loc[0, "sdb_data"], "14/05/2026")
        self.assertEqual(result.loc[0, "acm_data"], pd.Timestamp("2026-05-14"))


if __name__ == "__main__":
    unittest.main()
