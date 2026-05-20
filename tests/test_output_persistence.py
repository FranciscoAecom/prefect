import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch

import geopandas as gpd
from shapely.geometry import Point

from core.output.persistence import save_outputs


class OutputPersistenceTests(unittest.TestCase):
    @patch("core.output.persistence.write_output_gpkg")
    def test_autos_infracao_persists_complete_and_brazil_bbox_outputs(self, mock_write):
        record = SimpleNamespace(
            theme_folder="autos_infracao",
            input_path="entrada.gpkg",
            source_path="origem",
            rule_profile="auto_infracoes/autos_infracao",
        )
        gdf = gpd.GeoDataFrame(
            {
                "sdb_des_status": ["Lavrado", "Lavrado"],
                "geometry": [Point(-70.0, -9.0), Point(0.0, 50.0)],
            },
            geometry="geometry",
            crs="EPSG:4326",
        )

        with tempfile.TemporaryDirectory() as temp_dir:
            output_path = save_outputs(gdf, record, temp_dir)

        written_paths = [Path(call.args[1]).name for call in mock_write.call_args_list]
        self.assertEqual(len(mock_write.call_args_list), 2)
        self.assertIn(Path(output_path).name, written_paths)
        self.assertIn("entrada_validado_bbox_brasil.gpkg", written_paths)
        bbox_gdf = mock_write.call_args_list[1].args[0]
        self.assertEqual(len(bbox_gdf), 1)


if __name__ == "__main__":
    unittest.main()
