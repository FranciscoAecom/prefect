import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

import pandas as pd

from core.ingest import dictionary


class IngestDictionaryTests(unittest.TestCase):
    def setUp(self):
        dictionary._DICTIONARY_THEME_CACHE = None

    def tearDown(self):
        dictionary._DICTIONARY_THEME_CACHE = None

    def test_validate_uses_aecom_attribute_name(self):
        workbook_path = self._write_dictionary_workbook(
            [
                {
                    "theme": "Tema Teste",
                    "original_attribute_name": "cod_tema",
                    "aecom_attribute_name": "sdb_cod_tema",
                }
            ]
        )

        with patch.object(dictionary, "INGEST_WORKBOOK_PATH", workbook_path):
            result = dictionary.validate_theme_and_attributes(
                "Tema Teste",
                ["sdb_cod_tema"],
            )

        self.assertEqual(result["missing_attributes"], [])
        self.assertEqual(result["extra_attributes"], [])

    def test_dictionary_validation_ignores_generated_output_fields(self):
        workbook_path = self._write_dictionary_workbook(
            [
                {
                    "theme": "Tema Teste",
                    "original_attribute_name": "cod_tema",
                    "aecom_attribute_name": "sdb_cod_tema",
                },
                {
                    "theme": "Tema Teste",
                    "original_attribute_name": "acm_id",
                    "aecom_attribute_name": "acm_id",
                },
                {
                    "theme": "Tema Teste",
                    "original_attribute_name": "fid",
                    "aecom_attribute_name": "fid",
                },
            ]
        )

        with patch.object(dictionary, "INGEST_WORKBOOK_PATH", workbook_path):
            result = dictionary.validate_theme_and_attributes(
                "Tema Teste",
                ["sdb_cod_tema"],
            )

        self.assertEqual(result["missing_attributes"], [])
        self.assertEqual(result["extra_attributes"], [])

    def test_dictionary_validation_matches_raw_aecom_names_to_sdb_input_columns(self):
        workbook_path = self._write_dictionary_workbook(
            [
                {
                    "theme": "Tema Teste",
                    "original_attribute_name": "des_status",
                    "aecom_attribute_name": "des_status",
                }
            ]
        )

        with patch.object(dictionary, "INGEST_WORKBOOK_PATH", workbook_path):
            result = dictionary.validate_theme_and_attributes(
                "Tema Teste",
                ["sdb_des_status"],
            )

        self.assertEqual(result["missing_attributes"], [])
        self.assertEqual(result["extra_attributes"], [])

    def _write_dictionary_workbook(self, rows):
        temp_dir = tempfile.TemporaryDirectory()
        self.addCleanup(temp_dir.cleanup)
        workbook_path = Path(temp_dir.name) / "ingest.xlsx"
        pd.DataFrame(rows).to_excel(
            workbook_path,
            sheet_name="dictionaries",
            index=False,
        )
        return workbook_path


if __name__ == "__main__":
    unittest.main()
