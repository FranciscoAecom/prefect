from pathlib import Path
from types import SimpleNamespace
import unittest
from unittest.mock import patch

from core.treatment.run_loader import TreatmentRunContext
from core.treatment.run import run_treatment


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


class TreatmentRunTests(unittest.TestCase):
    def setUp(self):
        self.output_base = str(Path("tests") / "_tmp_output")

    @patch("core.treatment.run.run_treatment_record")
    @patch("core.treatment.run.prepare_treatment_run")
    def test_runs_each_record_with_group_state(
        self,
        mock_prepare_treatment_run,
        mock_run_treatment_record,
    ):
        records = [
            _record(2, 10, "rl_car_ac", "origem_a"),
            _record(2, 10, "rl_car_ac", "origem_a"),
        ]
        mock_prepare_treatment_run.return_value = TreatmentRunContext(
            records=records,
            output_dir=self.output_base,
        )

        run_treatment(output_base=self.output_base)

        mock_prepare_treatment_run.assert_called_once()
        self.assertEqual(mock_prepare_treatment_run.call_args.args, (self.output_base,))
        self.assertFalse(mock_prepare_treatment_run.call_args.kwargs["run_request"].force)
        self.assertEqual(mock_run_treatment_record.call_count, 2)
        self.assertIs(mock_run_treatment_record.call_args_list[0].args[0], records[0])
        self.assertIs(mock_run_treatment_record.call_args_list[1].args[0], records[1])
        self.assertEqual(mock_run_treatment_record.call_args_list[0].args[1], self.output_base)
        self.assertEqual(
            mock_run_treatment_record.call_args_list[0].kwargs,
            {"keep_individual_outputs_when_grouping": False},
        )

    @patch("core.treatment.run.run_treatment_record", side_effect=RuntimeError("boom"))
    @patch("core.treatment.run.prepare_treatment_run")
    def test_propagates_record_processing_errors(
        self,
        mock_prepare_treatment_run,
        mock_run_treatment_record,
    ):
        records = [_record(2, 10, "rl_car_ac", "origem_a")]
        mock_prepare_treatment_run.return_value = TreatmentRunContext(
            records=records,
            output_dir=self.output_base,
        )

        with self.assertRaisesRegex(RuntimeError, "boom"):
            run_treatment(output_base=self.output_base)

        mock_prepare_treatment_run.assert_called_once()
        self.assertEqual(mock_prepare_treatment_run.call_args.args, (self.output_base,))
        mock_run_treatment_record.assert_called_once()

    @patch("core.treatment.run.run_treatment_record")
    @patch("core.treatment.run.prepare_treatment_run", return_value=None)
    def test_returns_when_treatment_cannot_be_prepared(
        self,
        mock_prepare_treatment_run,
        mock_run_treatment_record,
    ):
        run_treatment(output_base=self.output_base)

        mock_prepare_treatment_run.assert_called_once()
        self.assertEqual(mock_prepare_treatment_run.call_args.args, (self.output_base,))
        mock_run_treatment_record.assert_not_called()


