import unittest

import geopandas as gpd
from shapely.geometry import Point

from core.processing.mandatory_pipeline import MANDATORY_FUNCTIONS, run_pipeline


class MandatoryPipelineTests(unittest.TestCase):
    def test_clean_whitespace_runs_as_mandatory_function(self):
        gdf = gpd.GeoDataFrame(
            {
                "sdb_des_status": ["  Lavrado   com   espaco  "],
                "geometry": [Point(0, 0)],
            },
            geometry="geometry",
            crs="EPSG:4326",
        )

        result, _stats = run_pipeline(gdf, mapping={})

        self.assertIn("clean_whitespace", MANDATORY_FUNCTIONS)
        self.assertEqual(result.loc[0, "sdb_des_status"], "Lavrado com espaco")


if __name__ == "__main__":
    unittest.main()
