import unittest
from types import SimpleNamespace
from unittest.mock import patch

from core.treatment.context_factory import build_treatment_context
from core.validation.session import ValidationSession


def _record():
    return SimpleNamespace(
        theme_folder="rl_car_ac",
        rule_profile="car_reserva_legal/rl_car_ac",
    )


class TreatmentContextFactoryTests(unittest.TestCase):
    @patch("core.treatment.context_factory.get_project_optional_functions")
    @patch("core.treatment.context_factory.resolve_project_config")
    def test_builds_treatment_context_from_record(
        self,
        mock_resolve_project_config,
        mock_get_project_optional_functions,
    ):
        record = _record()
        project_config = {"project_name": "car_reserva_legal"}
        optional_functions = {"validate_shapefile_attribute": object()}
        mock_resolve_project_config.return_value = project_config
        mock_get_project_optional_functions.return_value = optional_functions

        context = build_treatment_context(
            record,
            "tests/_tmp_output",
            id_start=5,
        )

        self.assertIs(context.record, record)
        self.assertEqual(context.output_dir, "tests/_tmp_output")
        self.assertEqual(context.project_config, project_config)
        self.assertEqual(context.rule_profile_name, record.rule_profile)
        self.assertIsNone(context.rule_profile)
        self.assertEqual(context.optional_functions, optional_functions)
        self.assertEqual(context.id_start, 5)
        self.assertIsInstance(context.validation_session, ValidationSession)
        mock_resolve_project_config.assert_called_once_with("rl_car_ac")
        mock_get_project_optional_functions.assert_called_once_with("car_reserva_legal")
