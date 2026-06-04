import unittest

import geopandas as gpd
from shapely.geometry import Point, Polygon

from core.treatment.steps.mandatory_pipeline import MANDATORY_FUNCTIONS, run_mandatory_treatments


class MandatoryTreatmentsTests(unittest.TestCase):
    def test_clean_whitespace_runs_as_mandatory_function(self):
        gdf = gpd.GeoDataFrame(
            {
                "sdb_des_status": ["  Lavrado   com   espaco  "],
                "geometry": [Point(0, 0)],
            },
            geometry="geometry",
            crs="EPSG:4326",
        )

        result, _stats = run_mandatory_treatments(gdf, mapping={})

        self.assertIn("clean_whitespace", MANDATORY_FUNCTIONS)
        self.assertEqual(result.loc[0, "sdb_des_status"], "Lavrado com espaco")

    def test_point_base_does_not_generate_area_or_perimeter_fields(self):
        gdf = gpd.GeoDataFrame(
            {
                "sdb_des_status": ["Lavrado"],
                "geometry": [Point(-47.0, -15.0)],
            },
            geometry="geometry",
            crs="EPSG:4326",
        )

        result, stats = run_mandatory_treatments(gdf, mapping={})

        self.assertNotIn("acm_a_ha", result.columns)
        self.assertNotIn("acm_prm_km", result.columns)
        self.assertIn("acm_long", result.columns)
        self.assertIn("acm_lat", result.columns)
        self.assertEqual(stats["skipped_point_measurements"], 1)

    def test_polygon_base_keeps_area_and_perimeter_fields(self):
        gdf = gpd.GeoDataFrame(
            {
                "sdb_des_status": ["Lavrado"],
                "geometry": [
                    Polygon(
                        [
                            (-47.0, -15.0),
                            (-47.0, -15.1),
                            (-47.1, -15.1),
                            (-47.1, -15.0),
                            (-47.0, -15.0),
                        ]
                    )
                ],
            },
            geometry="geometry",
            crs="EPSG:4326",
        )

        result, stats = run_mandatory_treatments(gdf, mapping={})

        self.assertIn("acm_a_ha", result.columns)
        self.assertIn("acm_prm_km", result.columns)
        self.assertEqual(stats["skipped_point_measurements"], 0)


if __name__ == "__main__":
    unittest.main()
