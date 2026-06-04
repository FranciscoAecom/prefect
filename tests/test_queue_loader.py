import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch

from core.ingest.run_request import IngestRunRequest
from core.treatment.queue_loader import TreatmentQueueRunContext, prepare_treatment_queue


def _record():
    return SimpleNamespace(
        sheet_row=2,
        record_id=10,
        theme_folder="rl_car_ac",
        source_path="origem_a",
    )


class QueueLoaderTests(unittest.TestCase):
    def setUp(self):
        self.output_base = str(Path("tests") / "_tmp_output")

    @patch("core.treatment.queue_loader.os.makedirs")
    @patch("core.treatment.queue_loader.export_queue_issues_report")
    @patch("core.treatment.queue_loader.log_queue_summary")
    @patch("core.treatment.queue_loader.load_treatment_queue")
    def test_prepares_queue_context(
        self,
        mock_load_treatment_queue,
        mock_log_queue_summary,
        mock_export_queue_issues_report,
        mock_makedirs,
    ):
        records = [_record()]
        summary = {"total_records": 1}
        issues = []
        mock_load_treatment_queue.return_value = (records, issues, summary)

        result = prepare_treatment_queue(self.output_base)

        self.assertEqual(
            result,
            TreatmentQueueRunContext(records=records, output_dir=self.output_base),
        )
        mock_log_queue_summary.assert_called_once_with(summary, issues)
        mock_export_queue_issues_report.assert_not_called()
        mock_makedirs.assert_called_once_with(self.output_base, exist_ok=True)

    @patch("core.treatment.queue_loader.log")
    @patch("core.treatment.queue_loader.export_queue_issues_report")
    @patch("core.treatment.queue_loader.log_queue_summary")
    @patch("core.treatment.queue_loader.load_treatment_queue")
    def test_returns_none_for_empty_queue(
        self,
        mock_load_treatment_queue,
        mock_log_queue_summary,
        mock_export_queue_issues_report,
        mock_log,
    ):
        summary = {"total_records": 0}
        issues = []
        mock_load_treatment_queue.return_value = ([], issues, summary)

        result = prepare_treatment_queue(self.output_base)

        self.assertIsNone(result)
        mock_log_queue_summary.assert_called_once_with(summary, issues)
        mock_export_queue_issues_report.assert_not_called()
        mock_log.assert_called_once_with("Nenhum arquivo elegivel encontrado para iniciar a esteira.")

    @patch("core.treatment.queue_loader.log")
    @patch("core.treatment.queue_loader.export_queue_issues_report")
    @patch("core.treatment.queue_loader.log_queue_summary")
    @patch("core.treatment.queue_loader.load_treatment_queue")
    def test_exports_queue_issues_report(
        self,
        mock_load_treatment_queue,
        _mock_log_queue_summary,
        mock_export_queue_issues_report,
        mock_log,
    ):
        records = [_record()]
        issue = SimpleNamespace(
            sheet_row=3,
            record_id=20,
            theme_folder="localidades",
            status="treatment",
            source_path="",
            code="missing_source_path",
            reason="caminho vazio",
        )
        mock_load_treatment_queue.return_value = (
            records,
            [issue],
            {"total_records": 1},
        )
        mock_export_queue_issues_report.return_value = (
            r"C:\tmp\queue_issues_20260526_154500.xlsx"
        )

        prepare_treatment_queue(self.output_base)

        mock_export_queue_issues_report.assert_called_once_with(
            [issue],
            self.output_base,
        )
        mock_log.assert_called_once_with(
            "Relatorio de issues da fila ingest gerado: "
            r"C:\tmp\queue_issues_20260526_154500.xlsx"
        )

    @patch("core.treatment.queue_loader.log")
    @patch("core.treatment.queue_loader.load_treatment_queue")
    def test_returns_none_when_queue_loading_fails(
        self,
        mock_load_treatment_queue,
        mock_log,
    ):
        mock_load_treatment_queue.side_effect = RuntimeError("boom")

        result = prepare_treatment_queue(self.output_base)

        self.assertIsNone(result)
        mock_log.assert_called_once_with("Erro ao carregar a fila ingest: boom")

    @patch("core.treatment.queue_loader.os.makedirs")
    @patch("core.treatment.queue_loader.log_queue_summary")
    @patch("core.treatment.queue_loader.load_treatment_queue")
    def test_passes_run_request_to_loader(
        self,
        mock_load_treatment_queue,
        _mock_log_queue_summary,
        _mock_makedirs,
    ):
        records = [_record()]
        mock_load_treatment_queue.return_value = (records, [], {"total_records": 1})
        run_request = IngestRunRequest.from_legacy(
            theme_folders=["localidades"],
            force=True,
        )

        prepare_treatment_queue(self.output_base, run_request=run_request)

        self.assertIs(mock_load_treatment_queue.call_args.kwargs["run_request"], run_request)
