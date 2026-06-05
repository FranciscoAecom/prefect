import unittest
from types import SimpleNamespace
from unittest.mock import patch

from core.reporting.log_summary import format_ingest_issue, log_summary


class LogSummaryTests(unittest.TestCase):
    @patch("core.reporting.log_summary.log")
    def test_logs_summary_rows_and_formatted_issues(self, mock_log):
        issue = SimpleNamespace(
            sheet_row=2,
            record_id=10,
            theme_folder="localidades",
            code="missing_source_path",
            reason="arquivo ausente",
        )

        log_summary(
            "Resumo teste",
            [("Registros lidos", 1)],
            issues_title="Excecoes teste",
            issues=[issue],
            format_issue=format_ingest_issue,
        )

        messages = [call.args[0] for call in mock_log.call_args_list]
        self.assertEqual(messages[0], "Resumo teste:")
        self.assertIn("  Registros lidos: 1", messages)
        self.assertIn("Excecoes teste:", messages)
        self.assertIn(
            "  Linha 2 | ID=10 | theme_folder=localidades | "
            "codigo=missing_source_path | motivo=arquivo ausente",
            messages,
        )


if __name__ == "__main__":
    unittest.main()
