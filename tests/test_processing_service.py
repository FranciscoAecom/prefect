import unittest
from types import SimpleNamespace
from unittest.mock import Mock, patch

import geopandas as gpd
from shapely.geometry import Point

from core.treatment.result import TreatmentRecordResult
from core.treatment.service import TreatmentService
from core.validation.session import ValidationSession


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


def _context(record):
    return SimpleNamespace(
        project_config={"project_name": "car_reserva_legal"},
        record=record,
        output_dir="tests/_tmp_output",
        rule_profile=None,
        rule_profile_name=record.rule_profile,
        optional_functions={},
        id_start=1,
        validation_session=ValidationSession(),
    )


def _gdf():
    return gpd.GeoDataFrame(
        {"coluna": ["A"], "geometry": [Point(0, 0)]},
        geometry="geometry",
        crs="EPSG:4326",
    )


class TreatmentServiceTests(unittest.TestCase):
    @patch("core.treatment.service.run_treatment_steps")
    @patch("core.treatment.service.build_treatment_context")
    def test_returns_zero_when_pipeline_fails(
        self,
        mock_build_treatment_context,
        mock_run_treatment_steps,
    ):
        record = _record()
        context = _context(record)
        mock_build_treatment_context.return_value = context
        mock_run_treatment_steps.return_value = None

        result = TreatmentService().process(record, output_dir="tests/_tmp_output")

        self.assertEqual(result, TreatmentRecordResult(0, None, None))
        mock_run_treatment_steps.assert_called_once()

    @patch("core.treatment.service.run_treatment_steps")
    @patch("core.treatment.service.build_treatment_context")
    def test_processes_record_and_returns_final_gdf(
        self,
        mock_build_treatment_context,
        mock_run_treatment_steps,
    ):
        record = _record()
        context = _context(record)
        final_gdf = _gdf()
        final_context = SimpleNamespace(
            **{
                **context.__dict__,
                "final_gdf": final_gdf,
                "output_path": "tests/_tmp_output/saida.gpkg",
            }
        )
        autofix_service = Mock()
        mock_build_treatment_context.return_value = context
        mock_run_treatment_steps.return_value = final_context

        result = TreatmentService(autofix_service=autofix_service).process(
            record,
            output_dir="tests/_tmp_output",
            id_start=5,
            use_configured_final_name=True,
            persist_individual_output=False,
        )

        self.assertEqual(result.processed_count, 1)
        self.assertEqual(result.output_path, "tests/_tmp_output/saida.gpkg")
        self.assertTrue(result.final_gdf.equals(final_gdf))
        mock_build_treatment_context.assert_called_once_with(
            record,
            "tests/_tmp_output",
            id_start=5,
        )
        mock_run_treatment_steps.assert_called_once_with(
            context,
            autofix_service,
            use_configured_final_name=True,
            persist_individual_output=False,
        )

    @patch("core.treatment.service.build_treatment_context")
    def test_returns_zero_when_context_build_fails(self, mock_build_treatment_context):
        record = _record()
        mock_build_treatment_context.side_effect = RuntimeError("config invalida")

        result = TreatmentService().process(record, output_dir="tests/_tmp_output")

        self.assertEqual(result, TreatmentRecordResult(0, None, None))
