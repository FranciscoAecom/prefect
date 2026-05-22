import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch

import geopandas as gpd
import pandas as pd
from shapely.geometry import Point

from core.metadata.xml import (
    build_data_dictionary_xml,
    format_xml_date,
    load_dictionary_descriptions,
    metadata_xml_name_for_base,
    metadata_xml_path_for_dataset,
    persist_bronze_metadata_xml,
    persist_silver_metadata_xml,
)


class MetadataXmlTests(unittest.TestCase):
    def test_data_dictionary_uses_original_descriptions_for_bronze(self):
        descriptions = {
            "tema teste": {
                "original": {"cod_tema": "Codigo original."},
                "aecom": {"sdb_cod_tema": "Codigo normalizado."},
            },
            "aecom": {
                "original": {"acm_id": "Identificador AECOM."},
                "aecom": {"acm_id": "Identificador AECOM."},
            },
        }
        record = SimpleNamespace(theme="Tema Teste")

        xml = build_data_dictionary_xml(
            ["cod_tema", "acm_id"],
            record=record,
            stage="bronze",
            descriptions=descriptions,
        )

        self.assertIn("<name>cod_tema</name>", xml)
        self.assertIn("<description>Codigo original.</description>", xml)
        self.assertIn("<name>acm_id</name>", xml)
        self.assertIn("<description>Identificador AECOM.</description>", xml)

    def test_data_dictionary_uses_aecom_descriptions_for_silver(self):
        descriptions = {
            "tema teste": {
                "original": {"cod_tema": "Codigo original."},
                "aecom": {"sdb_cod_tema": "Codigo normalizado."},
            }
        }
        record = SimpleNamespace(theme="Tema Teste")

        xml = build_data_dictionary_xml(
            ["sdb_cod_tema"],
            record=record,
            stage="silver",
            descriptions=descriptions,
        )

        self.assertIn("<name>sdb_cod_tema</name>", xml)
        self.assertIn("<description>Codigo normalizado.</description>", xml)

    @patch("core.metadata.xml.log")
    def test_missing_description_is_logged_and_kept_empty(self, mock_log):
        record = SimpleNamespace(theme="Tema Teste")

        xml = build_data_dictionary_xml(
            ["sdb_sem_descricao"],
            record=record,
            stage="silver",
            descriptions={},
        )

        self.assertIn("<name>sdb_sem_descricao</name>", xml)
        self.assertIn("<description></description>", xml)
        mock_log.assert_called_once()
        self.assertIn("Descricao de atributo nao encontrada", mock_log.call_args.args[0])

    def test_load_dictionary_descriptions_reads_expected_columns(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            workbook_path = Path(temp_dir) / "ingest.xlsx"
            pd.DataFrame(
                [
                    {
                        "theme": "Tema Teste",
                        "original_attribute_name": "cod_tema",
                        "aecom_attribute_name": "sdb_cod_tema",
                        "original_description": "Codigo original.",
                        "aecom_description": "Codigo normalizado.",
                    }
                ]
            ).to_excel(workbook_path, sheet_name="dictionaries", index=False)

            descriptions = load_dictionary_descriptions(workbook_path=workbook_path)

        self.assertEqual(
            descriptions["tema teste"]["original"]["cod_tema"],
            "Codigo original.",
        )
        self.assertEqual(
            descriptions["tema teste"]["aecom"]["sdb_cod_tema"],
            "Codigo normalizado.",
        )

    def test_persist_silver_metadata_xml_replaces_dictionary_block(self):
        gdf = gpd.GeoDataFrame(
            {"sdb_cod_tema": ["A"], "geometry": [Point(0, 0)]},
            geometry="geometry",
            crs="EPSG:4326",
        )
        record = SimpleNamespace(
            theme="Tema Teste",
            date="2026-05-22",
            citation="Fonte",
            category_acronym="pcd",
        )
        descriptions = {
            "tema teste": {
                "original": {"cod_tema": "Codigo original."},
                "aecom": {"sdb_cod_tema": "Codigo normalizado."},
            }
        }

        with tempfile.TemporaryDirectory() as temp_dir:
            output_path = Path(temp_dir) / "saida.gpkg"
            xml_path = persist_silver_metadata_xml(
                record,
                gdf,
                output_path,
                descriptions,
            )
            xml_text = xml_path.read_text(encoding="utf-8")

        self.assertIn("<data_dictionary>", xml_text)
        self.assertIn("<name>sdb_cod_tema</name>", xml_text)
        self.assertIn("<description>Codigo normalizado.</description>", xml_text)

    def test_metadata_xml_name_replaces_geometry_prefix_with_md(self):
        self.assertEqual(
            metadata_xml_name_for_base("pnt_pcd_enov_20260514"),
            "md_pcd_enov_20260514.xml",
        )
        self.assertEqual(
            metadata_xml_path_for_dataset(
                Path("saida") / "pnt_pcd_enov_20260514_bbox_brasil.gpkg"
            ),
            Path("saida") / "md_pcd_enov_20260514_bbox_brasil.xml",
        )
        self.assertEqual(
            metadata_xml_path_for_dataset(Path("saida") / "pol_pcd_rl_car_ac_20260301.shp"),
            Path("saida") / "md_pcd_rl_car_ac_20260301.xml",
        )
        self.assertEqual(
            metadata_xml_path_for_dataset(Path("saida") / "entrada_validado.gpkg"),
            Path("saida") / "md_entrada_validado.xml",
        )

    def test_xml_dates_are_formatted_without_time(self):
        self.assertEqual(format_xml_date("2026-05-14 00:00:00"), "2026-05-14")
        self.assertEqual(format_xml_date(pd.Timestamp("2021-09-15 00:00:00")), "2021-09-15")

    @patch("core.metadata.xml.inspect_dataset_fields")
    def test_bronze_xml_uses_same_metadata_name_as_silver(self, mock_inspect_fields):
        mock_inspect_fields.return_value = ["cod_tema", "geometry"]
        descriptions = {
            "tema teste": {
                "original": {"cod_tema": "Codigo original."},
                "aecom": {},
            }
        }
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_dir = Path(temp_dir)
            bronze_dir = temp_dir / "bronze"
            bronze_dir.mkdir()
            dataset_path = bronze_dir / "vw_brasil_adm_auto_infracao_p.shp"
            dataset_path.write_text("fake", encoding="utf-8")
            record = SimpleNamespace(
                theme="Tema Teste",
                date="2021-09-15 00:00:00",
                date_stamp="2026-05-14 00:00:00",
                beginposition="2021-09-15 00:00:00",
                bronze_dir=str(bronze_dir),
            )

            xml_path = persist_bronze_metadata_xml(
                record,
                dataset_path,
                descriptions,
                base_name="pnt_pcd_enov_20260514",
            )
            xml_text = xml_path.read_text(encoding="utf-8")

        self.assertEqual(xml_path.name, "md_pcd_enov_20260514.xml")
        self.assertIn("<gco:DateTime>2026-05-14</gco:DateTime>", xml_text)
        self.assertIn("<gco:DateTime>2021-09-15</gco:DateTime>", xml_text)
        self.assertIn("<gml:beginPosition>2021-09-15</gml:beginPosition>", xml_text)
        self.assertNotIn("00:00:00", xml_text)


if __name__ == "__main__":
    unittest.main()
