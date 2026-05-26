import unittest
from unittest.mock import patch

import pandas as pd

from core.ingest.repository import ExcelIngestRepository, IngestCatalogRow


class IngestRepositoryTests(unittest.TestCase):
    @patch("core.ingest.repository.pd.read_excel")
    def test_excel_repository_iterates_rows_with_sheet_numbers(self, mock_read_excel):
        mock_read_excel.return_value = pd.DataFrame(
            [
                {"ID": 10, "theme_folder": "localidades"},
                {"ID": 11, "theme_folder": "estado"},
            ]
        )
        repository = ExcelIngestRepository("planilha.xlsx", "datas")

        rows = list(repository.iter_rows())

        self.assertEqual([row.sheet_row for row in rows], [2, 3])
        self.assertEqual([row.get("theme_folder") for row in rows], ["localidades", "estado"])
        mock_read_excel.assert_called_once_with("planilha.xlsx", sheet_name="datas")

    def test_catalog_row_uses_default_for_missing_value(self):
        row = IngestCatalogRow(sheet_row=2, data={"theme_folder": "localidades"})

        self.assertEqual(row.get("status", "missing"), "missing")


if __name__ == "__main__":
    unittest.main()
