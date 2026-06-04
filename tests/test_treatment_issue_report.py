import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch

from core.treatment.issue_report import export_treatment_issues_report


class TreatmentIssueReportTests(unittest.TestCase):
    def test_exports_treatment_issues_to_xlsx(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            issue = SimpleNamespace(
                sheet_row=2,
                record_id=10,
                theme_folder="localidades",
                status="treatment",
                source_path=r"L:\base.gpkg",
                code="missing_rule_profile",
                reason="perfil ausente",
            )

            path = export_treatment_issues_report(
                [issue],
                temp_dir,
                timestamp="20260526_154500",
            )

            self.assertEqual(
                path,
                str(Path(temp_dir) / "treatment_issues_20260526_154500.xlsx"),
            )
            self.assertTrue(Path(path).exists())

    @patch("core.treatment.issue_report.pd.DataFrame.to_excel", side_effect=RuntimeError("xlsx"))
    def test_falls_back_to_csv_when_xlsx_fails(self, _mock_to_excel):
        with tempfile.TemporaryDirectory() as temp_dir:
            issue = SimpleNamespace(
                sheet_row=2,
                record_id=10,
                theme_folder="localidades",
                status="treatment",
                source_path=r"L:\base.gpkg",
                code="missing_rule_profile",
                reason="perfil ausente",
            )

            path = export_treatment_issues_report(
                [issue],
                temp_dir,
                timestamp="20260526_154500",
            )

            self.assertEqual(
                path,
                str(Path(temp_dir) / "treatment_issues_20260526_154500.csv"),
            )
            self.assertTrue(Path(path).exists())


if __name__ == "__main__":
    unittest.main()

