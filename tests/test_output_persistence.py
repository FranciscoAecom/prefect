import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch

import geopandas as gpd
from shapely.geometry import Point

from core.silver.persistence import save_outputs


class OutputPersistenceTests(unittest.TestCase):
    @patch("core.output.secondary_outputs.write_output_gpkg")
    @patch("core.silver.persistence.write_output_gpkg")
    def test_configured_profile_persists_complete_and_brazil_bbox_outputs(
        self,
        mock_main_write,
        mock_secondary_write,
    ):
        record = SimpleNamespace(
            theme_folder="autos_infracao",
            input_path="entrada.gpkg",
            source_path="origem",
            rule_profile="autos_infracao/autos_infracao",
        )
        gdf = gpd.GeoDataFrame(
            {
                "sdb_des_status": ["Lavrado", "Lavrado"],
                "geometry": [Point(-70.0, -9.0), Point(0.0, 50.0)],
            },
            geometry="geometry",
            crs="EPSG:4326",
        )
        rule_profile = {"secondary_outputs": ["brazil_bbox"]}

        with tempfile.TemporaryDirectory() as temp_dir:
            output_path = save_outputs(gdf, record, temp_dir, rule_profile=rule_profile)

        self.assertEqual(mock_main_write.call_count, 1)
        self.assertEqual(mock_secondary_write.call_count, 1)
        self.assertEqual(Path(output_path).name, "entrada_validado.gpkg")
        self.assertEqual(
            Path(mock_secondary_write.call_args.args[1]).name,
            "entrada_validado_bbox_brasil.gpkg",
        )
        bbox_gdf = mock_secondary_write.call_args.args[0]
        self.assertEqual(len(bbox_gdf), 1)

    @patch("core.output.secondary_outputs.write_output_gpkg")
    @patch("core.silver.persistence.write_output_gpkg")
    def test_secondary_outputs_are_skipped_without_profile_configuration(
        self,
        mock_main_write,
        mock_secondary_write,
    ):
        record = SimpleNamespace(
            theme_folder="autos_infracao",
            input_path="entrada.gpkg",
            source_path="origem",
            rule_profile="autos_infracao/autos_infracao",
        )
        gdf = gpd.GeoDataFrame(
            {"geometry": [Point(-70.0, -9.0)]},
            geometry="geometry",
            crs="EPSG:4326",
        )

        with tempfile.TemporaryDirectory() as temp_dir:
            save_outputs(gdf, record, temp_dir, rule_profile={})

        self.assertEqual(mock_main_write.call_count, 1)
        mock_secondary_write.assert_not_called()


if __name__ == "__main__":
    unittest.main()
