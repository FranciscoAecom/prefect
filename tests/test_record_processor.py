import unittest
from types import SimpleNamespace
from unittest.mock import patch

from core.treatment.result import TreatmentRecordResult
from core.treatment.record_processor import process_treatment_record


def _record():
    return SimpleNamespace(
        sheet_row=2,
        record_id=10,
        theme="tema_teste",
        theme_folder="rl_car_ac",
        status="treatment",
        source_path="origem_a",
        input_path="origem_a.gpkg",
        rule_profile="car_reserva_legal/rl_car_ac",
    )


class TreatmentRecordProcessorTests(unittest.TestCase):
    @patch("core.treatment.record_processor.TreatmentService")
    def test_delegates_to_treatment_service(self, mock_service_cls):
        record = _record()
        mock_service = mock_service_cls.return_value
        mock_service.process.return_value = TreatmentRecordResult(1, "saida.gpkg", "gdf")

        result = process_treatment_record(
            record,
            output_dir="tests/_tmp_output",
            id_start=5,
            use_configured_final_name=True,
            persist_individual_output=False,
        )

        self.assertEqual(result, TreatmentRecordResult(1, "saida.gpkg", "gdf"))
        mock_service.process.assert_called_once_with(
            record,
            "tests/_tmp_output",
            id_start=5,
            use_configured_final_name=True,
            persist_individual_output=False,
        )
