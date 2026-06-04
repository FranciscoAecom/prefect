import unittest
from types import SimpleNamespace
from unittest.mock import patch

from core.treatment.dispatcher import process_treatment_record_by_dataset_kind


class ProcessingDispatcherTests(unittest.TestCase):
    @patch("core.treatment.dispatcher.process_vector_treatment_record")
    def test_dispatches_vector_records_to_vector_processor(self, mock_process_record):
        record = SimpleNamespace(dataset_kind="vector")
        group_state = SimpleNamespace(
            id_start_for=lambda _record: 7,
            use_configured_final_name=lambda _record: True,
            persist_individual_output=lambda _record, _keep: False,
        )
        mock_process_record.return_value = "vector-result"

        result = process_treatment_record_by_dataset_kind(
            record,
            "out",
            group_state,
            keep_individual_outputs_when_grouping=False,
        )

        self.assertEqual(result, "vector-result")
        mock_process_record.assert_called_once_with(
            record,
            "out",
            id_start=7,
            use_configured_final_name=True,
            persist_individual_output=False,
        )

    @patch("core.treatment.dispatcher.process_raster_treatment_record")
    @patch("core.treatment.dispatcher.process_vector_treatment_record")
    def test_dispatches_raster_records_to_raster_processor(
        self,
        mock_process_record,
        mock_process_raster_record,
    ):
        record = SimpleNamespace(dataset_kind="raster")
        group_state = SimpleNamespace(
            use_configured_final_name=lambda _record: True,
        )
        mock_process_raster_record.return_value = "raster-result"

        result = process_treatment_record_by_dataset_kind(
            record,
            "out",
            group_state,
            keep_individual_outputs_when_grouping=False,
        )

        self.assertEqual(result, "raster-result")
        mock_process_raster_record.assert_called_once_with(
            record,
            "out",
            use_configured_final_name=True,
        )
        mock_process_record.assert_not_called()


if __name__ == "__main__":
    unittest.main()
