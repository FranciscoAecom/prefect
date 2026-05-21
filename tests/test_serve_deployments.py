import unittest
from unittest.mock import patch

from core.prefect_support.deployment_names import (
    AUTO_INFRACOES_PROCESSING_DEPLOYMENT_NAME,
    AUTO_INFRACOES_PROCESSING_QUALIFIED_DEPLOYMENT_NAME,
)
from scripts import serve


class ServeDeploymentsTest(unittest.TestCase):
    @patch("scripts.serve.start_scheduled_run_renamer")
    @patch("scripts.serve.data_pipeline_flow.serve")
    def test_auto_infracoes_serves_with_fixed_theme_folder(
        self,
        mock_serve,
        mock_start_renamer,
    ):
        serve.serve_auto_infracoes()

        mock_start_renamer.assert_called_once_with(
            deployment_name=AUTO_INFRACOES_PROCESSING_QUALIFIED_DEPLOYMENT_NAME,
            interval_seconds=5,
        )
        mock_serve.assert_called_once()
        _, kwargs = mock_serve.call_args

        self.assertEqual(kwargs["name"], AUTO_INFRACOES_PROCESSING_DEPLOYMENT_NAME)
        self.assertEqual(kwargs["parameters"], {"theme_folders": ["autos_infracao"]})
        self.assertIn("auto_infracoes", kwargs["tags"])


if __name__ == "__main__":
    unittest.main()
