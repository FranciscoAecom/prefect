import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch

import geopandas as gpd
import pandas as pd
from shapely.geometry import Point

from core.silver.persistence import save_outputs, save_outputs_manifest
from core.spatial.brazil_bounds import brazil_bounds_centroid


class OutputPersistenceTests(unittest.TestCase):
    @patch("core.silver.persistence.write_output_gpkg")
    def test_output_adjustments_relocates_outside_brazil_bounds_to_centroid(
        self,
        mock_main_write,
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
        rule_profile = {
            "output_adjustments": {
                "relocate_outside_brazil_bounds_to_centroid": True,
            },
        }

        with tempfile.TemporaryDirectory() as temp_dir:
            output_path = save_outputs(gdf, record, temp_dir, rule_profile=rule_profile)

        self.assertEqual(mock_main_write.call_count, 1)
        self.assertEqual(Path(output_path).name, "entrada_validado.gpkg")

        main_gdf = mock_main_write.call_args.args[0]
        self.assertEqual(len(main_gdf), 2)
        self.assertNotEqual(main_gdf.loc[1, "geometry"], Point(0.0, 50.0))
        self.assertIn("acm_long_centroide_brasil", main_gdf.columns)
        self.assertIn("acm_lat_centroide_brasil", main_gdf.columns)
        self.assertTrue(pd.isna(main_gdf.loc[0, "acm_long_centroide_brasil"]))
        centroid = brazil_bounds_centroid("EPSG:4326")
        self.assertEqual(main_gdf.loc[1, "acm_long_centroide_brasil"], round(centroid.x, 6))
        self.assertEqual(main_gdf.loc[1, "acm_lat_centroide_brasil"], round(centroid.y, 6))

    @patch("core.silver.persistence.write_output_gpkg")
    def test_single_output_is_persisted_without_profile_configuration(
        self,
        mock_main_write,
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

    @patch("core.silver.persistence.persist_silver_artifacts")
    @patch("core.silver.persistence.write_output_gpkg")
    def test_save_outputs_manifest_collects_outputs_and_artifacts(
        self,
        _mock_main_write,
        mock_artifacts,
    ):
        mock_artifacts.return_value = (
            [Path("saida") / "md_entrada_validado.xml"],
            [Path("saida") / "sld_entrada_validado.sld"],
        )
        record = SimpleNamespace(
            theme_folder="autos_infracao",
            input_path="entrada.gpkg",
            source_path="origem",
            rule_profile="autos_infracao/autos_infracao",
        )
        gdf = gpd.GeoDataFrame(
            {
                "sdb_codigo": ["A"],
                "geometry": [Point(-70.0, -9.0)],
            },
            geometry="geometry",
            crs="EPSG:4326",
        )
        rule_profile = {
            "quality_outputs": {
                "attribute_duplicates": False,
                "geometric_duplicates": False,
                "ogc_invalid_geometries": False,
            },
        }

        with tempfile.TemporaryDirectory() as temp_dir:
            manifest = save_outputs_manifest(
                gdf,
                record,
                temp_dir,
                rule_profile=rule_profile,
            )

        self.assertEqual(manifest.primary_output.path.name, "entrada_validado.gpkg")
        self.assertEqual(
            [path.name for path in manifest.xml_files],
            ["md_entrada_validado.xml"],
        )
        self.assertEqual(
            [path.name for path in manifest.sld_files],
            ["sld_entrada_validado.sld"],
        )
        self.assertEqual(
            manifest.quality_reports,
            {
                "attribute_duplicates": None,
                "geometric_duplicates": None,
                "ogc_invalid_geometries": None,
            },
        )
        self.assertEqual(manifest.manifest_path.name, "entrada_validado_manifest.json")

    @patch("core.silver.persistence.persist_silver_artifacts")
    @patch("core.silver.persistence.write_output_gpkg")
    def test_save_outputs_manifest_does_not_persist_manifest_when_dataset_skipped(
        self,
        _mock_main_write,
        mock_artifacts,
    ):
        mock_artifacts.return_value = ([], [])
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
            manifest = save_outputs_manifest(
                gdf,
                record,
                temp_dir,
                persist_dataset=False,
                rule_profile={},
            )

        self.assertIsNone(manifest.primary_output)
        self.assertIsNone(manifest.manifest_path)
        self.assertFalse((Path(temp_dir) / "entrada_validado_manifest.json").exists())


if __name__ == "__main__":
    unittest.main()
