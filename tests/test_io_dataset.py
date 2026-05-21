import tempfile
import unittest
from pathlib import Path
import gc

import geopandas as gpd
import pandas as pd
import pyogrio
from shapely.geometry import Point

from core.io.dataset import write_output_gpkg


class WriteOutputGpkgTest(unittest.TestCase):
    def test_date_only_datetime_columns_are_written_as_gpkg_date(self):
        with tempfile.TemporaryDirectory() as tmp:
            output = Path(tmp) / "datas.gpkg"
            gdf = gpd.GeoDataFrame(
                {
                    "acm_data": [
                        pd.Timestamp("2026-05-21"),
                        pd.NaT,
                    ],
                    "acm_data_hora": [
                        pd.Timestamp("2026-05-21 10:30:00"),
                        pd.NaT,
                    ],
                },
                geometry=[Point(0, 0), Point(1, 1)],
                crs="EPSG:4326",
            )

            write_output_gpkg(gdf, output)

            info = pyogrio.read_info(output)
            field_types = dict(zip(info["fields"], info["ogr_types"]))

            self.assertEqual(field_types["acm_data"], "OFTDate")
            self.assertEqual(field_types["acm_data_hora"], "OFTDateTime")
            del info
            gc.collect()


if __name__ == "__main__":
    unittest.main()
