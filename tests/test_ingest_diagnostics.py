import unittest
from unittest.mock import patch

import pandas as pd

from core.ingest.diagnostics import (
    diagnose_ingest_theme,
    format_ingest_theme_diagnostic,
)


class IngestDiagnosticsTests(unittest.TestCase):
    @patch("core.ingest.diagnostics.Path.exists", return_value=True)
    @patch("core.ingest.diagnostics.find_rule_profile_by_theme_folder")
    @patch("core.ingest.diagnostics.pd.read_excel")
    def test_diagnoses_non_eligible_status(
        self,
        mock_read_excel,
        mock_find_profile,
        _mock_path_exists,
    ):
        mock_read_excel.return_value = pd.DataFrame(
            [
                {
                    "ID": 1,
                    "theme": "Localidades",
                    "theme_folder": "localidades",
                    "status": "Complete",
                    "path_shapefile_temp": r"L:\base.gpkg",
                }
            ]
        )
        mock_find_profile.return_value = "localidades/localidades"

        diagnostic = diagnose_ingest_theme("localidades")
        lines = format_ingest_theme_diagnostic(diagnostic)

        self.assertEqual(len(diagnostic["matches"]), 1)
        self.assertFalse(diagnostic["matches"][0]["status_eligible"])
        self.assertIn("    status: Complete | elegivel: nao", lines)
        self.assertIn(
            "    motivo: status fora dos elegiveis para processamento.",
            lines,
        )

    @patch("core.ingest.diagnostics.pd.read_excel")
    def test_diagnoses_missing_theme_folder(self, mock_read_excel):
        mock_read_excel.return_value = pd.DataFrame(
            [{"theme_folder": "estado", "status": "Waiting Update"}]
        )

        diagnostic = diagnose_ingest_theme("localidades")
        lines = format_ingest_theme_diagnostic(diagnostic)

        self.assertEqual(diagnostic["matches"], [])
        self.assertIn("  Nenhuma linha encontrada para esse theme_folder.", lines)


if __name__ == "__main__":
    unittest.main()
