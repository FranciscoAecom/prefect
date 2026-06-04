import unittest
from unittest.mock import patch

from core.prefect_support.deployment_names import (
    AUTOS_INFRACAO_TREATMENT_DEPLOYMENT_NAME,
    AUTOS_INFRACAO_TREATMENT_QUALIFIED_DEPLOYMENT_NAME,
    DATA_PUBLISH_DEPLOYMENT_NAME,
)
from scripts import serve


class ServeDeploymentsTest(unittest.TestCase):
    @patch("scripts.serve.start_scheduled_run_renamer")
    @patch("scripts.serve.data_treatment_flow.serve")
    def test_autos_infracao_serves_with_fixed_theme_folder(
        self,
        mock_serve,
        mock_start_renamer,
    ):
        serve.serve_autos_infracao()

        mock_start_renamer.assert_called_once_with(
            deployment_name=AUTOS_INFRACAO_TREATMENT_QUALIFIED_DEPLOYMENT_NAME,
            interval_seconds=5,
        )
        mock_serve.assert_called_once()
        _, kwargs = mock_serve.call_args

        self.assertEqual(kwargs["name"], AUTOS_INFRACAO_TREATMENT_DEPLOYMENT_NAME)
        self.assertEqual(kwargs["parameters"], {"theme_folders": ["autos_infracao"]})
        self.assertIn("autos_infracao", kwargs["tags"])
        self.assertIn("treatment", kwargs["tags"])

    @patch("scripts.serve.data_publish_flow.serve")
    def test_data_publish_serves_publish_deployment(self, mock_serve):
        serve.serve_data_publish()

        mock_serve.assert_called_once()
        _, kwargs = mock_serve.call_args
        self.assertEqual(kwargs["name"], DATA_PUBLISH_DEPLOYMENT_NAME)
        self.assertIn("geoserver", kwargs["tags"])
        self.assertIn("geonetwork", kwargs["tags"])

    @patch("scripts.serve.build_ingest_scheduled_treatment_schedules")
    @patch("scripts.serve.start_scheduled_run_renamer")
    @patch("scripts.serve.data_treatment_flow.serve")
    def test_scheduled_treatment_serves_ingest_schedules(
        self,
        mock_serve,
        mock_start_renamer,
        mock_build_schedules,
    ):
        mock_build_schedules.return_value = ["schedule"]

        serve.serve_scheduled_treatment()

        mock_start_renamer.assert_called_once_with(
            deployment_name="Data Treatment/Treatment Agendado pela Ingest",
            interval_seconds=5,
        )
        mock_build_schedules.assert_called_once_with()
        mock_serve.assert_called_once()
        _, kwargs = mock_serve.call_args
        self.assertEqual(kwargs["name"], "Treatment Agendado pela Ingest")
        self.assertEqual(kwargs["schedules"], ["schedule"])
        self.assertIn("ingest", kwargs["tags"])

if __name__ == "__main__":
    unittest.main()
