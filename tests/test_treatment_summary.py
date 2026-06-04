import unittest
from types import SimpleNamespace
from unittest.mock import patch

from core.treatment.summary import log_treatment_summary


class TreatmentSummaryTests(unittest.TestCase):
    @patch("core.treatment.summary.log")
    def test_logs_treatment_summary_and_issues(self, mock_log):
        summary = {
            "total_records": 2,
            "ready_candidates": 1,
            "eligible_records": 1,
            "issues": 1,
            "treatment_statuses": ["treatment", "treatment"],
        }
        issues = [
            SimpleNamespace(
                sheet_row=3,
                record_id=20,
                theme_folder="",
                code="missing_source_path",
                reason="arquivo ausente",
            )
        ]

        log_treatment_summary(summary, issues)

        messages = [call.args[0] for call in mock_log.call_args_list]
        self.assertIn("Resumo da planilha ingest:", messages)
        self.assertIn("  Registros lidos: 2", messages)
        self.assertIn(
            "  Status elegiveis: treatment, treatment",
            messages,
        )
        self.assertIn("Excecoes encontradas para tratamento:", messages)
        self.assertIn(
            "  Linha 3 | ID=20 | theme_folder=<vazio> | "
            "codigo=missing_source_path | motivo=arquivo ausente",
            messages,
        )

    @patch("core.treatment.summary.log")
    def test_logs_treatment_issue_without_code(self, mock_log):
        summary = {
            "total_records": 1,
            "ready_candidates": 1,
            "eligible_records": 0,
            "issues": 1,
        }
        issues = [
            SimpleNamespace(
                sheet_row=2,
                record_id=10,
                theme_folder="localidades",
                reason="erro legado",
            )
        ]

        log_treatment_summary(summary, issues)

        messages = [call.args[0] for call in mock_log.call_args_list]
        self.assertIn(
            "  Linha 2 | ID=10 | theme_folder=localidades | motivo=erro legado",
            messages,
        )

