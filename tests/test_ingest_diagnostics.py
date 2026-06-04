import unittest
from unittest.mock import patch

import pandas as pd

from core.ingest.diagnostics import (
    diagnose_ingest_theme,
    format_ingest_theme_diagnostic,
)
from core.rules.catalog import RuleProfileResolution


class IngestDiagnosticsTests(unittest.TestCase):
    @patch("core.ingest.diagnostics.Path.exists", return_value=True)
    @patch("core.ingest.diagnostics.resolve_rule_profile_for_theme")
    @patch("core.ingest.repository.pd.read_excel")
    def test_diagnoses_non_eligible_status(
        self,
        mock_read_excel,
        mock_resolve_rule_profile,
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
        mock_resolve_rule_profile.return_value = RuleProfileResolution(
            theme_folder="localidades",
            normalized_theme_folder="localidades",
            project_name="localidades",
            expected_profile_name="localidades/localidades",
            profile_name="localidades/localidades",
            profile_dir=None,
            profile_project_name="localidades",
        )

        diagnostic = diagnose_ingest_theme("localidades")
        lines = format_ingest_theme_diagnostic(diagnostic)

        self.assertEqual(len(diagnostic["matches"]), 1)
        self.assertFalse(diagnostic["matches"][0]["status_eligible"])
        self.assertIn(
            "invalid_status_flags",
            diagnostic["matches"][0]["issue_codes"],
        )
        self.assertIn("    status: Complete | elegivel: nao", lines)
        self.assertIn("    codigos: invalid_status_flags", lines)
        self.assertIn(
            "    motivo: status contem flags invalidas.",
            lines,
        )

    @patch("core.ingest.repository.pd.read_excel")
    def test_diagnoses_missing_theme_folder(self, mock_read_excel):
        mock_read_excel.return_value = pd.DataFrame(
            [{"theme_folder": "estado", "status": "treatment"}]
        )

        diagnostic = diagnose_ingest_theme("localidades")
        lines = format_ingest_theme_diagnostic(diagnostic)

        self.assertEqual(diagnostic["matches"], [])
        self.assertIn("  Nenhuma linha encontrada para esse theme_folder.", lines)


if __name__ == "__main__":
    unittest.main()
