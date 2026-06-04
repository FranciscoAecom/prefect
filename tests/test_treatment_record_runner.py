import unittest
from types import SimpleNamespace
from unittest.mock import call, patch

from core.treatment.result import TreatmentRecordResult
from core.treatment.group_state import TreatmentGroupState
from core.treatment.record_runner import run_treatment_record


def _record(sheet_row, record_id, theme_folder, source_path):
    return SimpleNamespace(
        sheet_row=sheet_row,
        record_id=record_id,
        theme="tema_teste",
        status="treatment",
        theme_folder=theme_folder,
        source_path=source_path,
        input_path=f"{source_path}.gpkg",
        rule_profile=f"{theme_folder}/{theme_folder}",
    )


class QueueRecordRunnerTests(unittest.TestCase):
    @patch("core.treatment.record_runner.clear_context_log")
    @patch("core.treatment.record_runner.append_group_consolidated_output")
    @patch("core.treatment.record_runner.process_treatment_record_by_dataset_kind")
    @patch("core.treatment.record_runner.set_context_log")
    def test_processes_record_and_updates_group_state(
        self,
        mock_set_context_log,
        mock_process_by_kind,
        mock_append_group_consolidated_output,
        mock_clear_context_log,
    ):
        records = [
            _record(2, 10, "rl_car_ac", "origem_a"),
            _record(2, 10, "rl_car_ac", "origem_a"),
        ]
        group_state = TreatmentGroupState(records, enable_group_consolidation=True)
        mock_process_by_kind.side_effect = [
            TreatmentRecordResult(3, None, "gdf1"),
            TreatmentRecordResult(2, None, "gdf2"),
        ]

        run_treatment_record(
            records[0],
            "tests/_tmp_output",
            group_state,
            keep_individual_outputs_when_grouping=False,
        )
        run_treatment_record(
            records[1],
            "tests/_tmp_output",
            group_state,
            keep_individual_outputs_when_grouping=False,
        )

        self.assertEqual(mock_process_by_kind.call_count, 2)
        self.assertEqual(
            mock_append_group_consolidated_output.call_args_list,
            [
                call(records[0], "gdf1", "tests/_tmp_output", append=False),
                call(records[1], "gdf2", "tests/_tmp_output", append=True),
            ],
        )
        self.assertEqual(mock_set_context_log.call_count, 2)
        self.assertEqual(mock_clear_context_log.call_count, 2)

    @patch("core.treatment.record_runner.clear_context_log")
    @patch("core.treatment.record_runner.process_treatment_record_by_dataset_kind", side_effect=RuntimeError("boom"))
    @patch("core.treatment.record_runner.set_context_log")
    def test_clears_context_log_even_when_record_processing_fails(
        self,
        mock_set_context_log,
        mock_process_by_kind,
        mock_clear_context_log,
    ):
        record = _record(2, 10, "rl_car_ac", "origem_a")
        group_state = TreatmentGroupState([record], enable_group_consolidation=True)

        with self.assertRaisesRegex(RuntimeError, "boom"):
            run_treatment_record(
                record,
                "tests/_tmp_output",
                group_state,
                keep_individual_outputs_when_grouping=False,
            )

        mock_set_context_log.assert_called_once()
        mock_process_by_kind.assert_called_once()
        mock_clear_context_log.assert_called_once()

    @patch("core.treatment.record_runner.clear_context_log")
    @patch("core.treatment.record_runner.process_treatment_record_by_dataset_kind")
    @patch("core.treatment.record_runner.set_context_log")
    def test_delegates_processing_to_dispatcher(
        self,
        mock_set_context_log,
        mock_process_by_kind,
        mock_clear_context_log,
    ):
        record = _record(2, 10, "raster_precipitacao", "chuva")
        record.dataset_kind = "raster"
        record.input_path = "chuva.tif"
        group_state = TreatmentGroupState([record], enable_group_consolidation=True)
        mock_process_by_kind.return_value = TreatmentRecordResult(
            processed_count=1,
            output_path="saida.tif",
            final_gdf=None,
        )

        run_treatment_record(
            record,
            "tests/_tmp_output",
            group_state,
            keep_individual_outputs_when_grouping=False,
        )

        mock_process_by_kind.assert_called_once_with(
            record,
            "tests/_tmp_output",
            group_state,
            False,
        )
        mock_set_context_log.assert_called_once()
        mock_clear_context_log.assert_called_once()

