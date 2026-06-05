import unittest
from unittest.mock import patch

from core.prefect_support.deployment_names import (
    DATA_PUBLISH_DEPLOYMENT_NAME,
    SCHEDULED_TREATMENT_DEPLOYMENT_NAME,
    SCHEDULED_TREATMENT_QUALIFIED_DEPLOYMENT_NAME,
)
from scripts import serve


class ServeDeploymentsTest(unittest.TestCase):
    @patch("scripts.serve.data_publish_flow.serve")
    def test_data_publish_serves_publish_deployment(self, mock_serve):
        serve.serve_data_publish()

        mock_serve.assert_called_once()
        _, kwargs = mock_serve.call_args
        self.assertEqual(kwargs["name"], DATA_PUBLISH_DEPLOYMENT_NAME)
        self.assertIn("geoserver", kwargs["tags"])
        self.assertIn("geonetwork", kwargs["tags"])

    @patch("scripts.serve.build_treatment_schedules")
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
            deployment_name=SCHEDULED_TREATMENT_QUALIFIED_DEPLOYMENT_NAME,
            interval_seconds=5,
        )
        mock_build_schedules.assert_called_once_with()
        mock_serve.assert_called_once()
        _, kwargs = mock_serve.call_args
        self.assertEqual(kwargs["name"], SCHEDULED_TREATMENT_DEPLOYMENT_NAME)
        self.assertEqual(kwargs["schedules"], ["schedule"])
        self.assertIn("ingest", kwargs["tags"])

if __name__ == "__main__":
    unittest.main()
