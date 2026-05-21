import unittest
import inspect
from unittest.mock import patch

from core.downloads.flow import data_download_flow


class DownloadFlowTests(unittest.TestCase):
    def test_flow_signature_does_not_expose_manual_dataset_parameters(self):
        signature = inspect.signature(data_download_flow.fn)

        self.assertNotIn("dataset_key", signature.parameters)
        self.assertNotIn("region", signature.parameters)
        self.assertIn("theme_folders", signature.parameters)

    @patch("core.downloads.flow.data_pipeline_flow")
    @patch("core.downloads.flow.emit_dataset_downloaded_event_task")
    @patch("core.downloads.flow.extract_download_task")
    @patch("core.downloads.flow.download_dataset_task")
    @patch("core.downloads.flow.load_download_queue_task")
    def test_default_flow_uses_download_queue(
        self,
        mock_load_queue,
        mock_download,
        mock_extract,
        mock_emit_event,
        mock_pipeline,
    ):
        mock_load_queue.return_value = [
            {"dataset_key": "car_app", "region": "AC"},
            {"dataset_key": "car_uso_restrito", "region": "ES"},
        ]
        mock_download.side_effect = [
            {"archive_path": "app.zip", "theme_folder": "app_car_ac"},
            {"archive_path": "ur.zip", "theme_folder": "ur_car_es"},
        ]
        mock_extract.side_effect = [
            {
                "archive_path": "app.zip",
                "theme_folder": "app_car_ac",
                "extract_dir": "input/downloads/app_car_ac",
                "dataset_key": "car_app",
                "connector": "car_public_api",
                "region": "AC",
            },
            {
                "archive_path": "ur.zip",
                "theme_folder": "ur_car_es",
                "extract_dir": "input/downloads/ur_car_es",
                "dataset_key": "car_uso_restrito",
                "connector": "car_public_api",
                "region": "ES",
            },
        ]

        result = data_download_flow.fn()

        mock_load_queue.assert_called_once_with(theme_folders=None)
        self.assertEqual(mock_download.call_count, 2)
        self.assertEqual(mock_extract.call_count, 2)
        self.assertEqual(mock_emit_event.call_count, 2)
        self.assertEqual(mock_pipeline.call_count, 2)
        self.assertEqual(len(result), 2)
        self.assertEqual(
            mock_pipeline.call_args_list[0].kwargs["theme_folders"],
            ["app_car_ac"],
        )
        self.assertEqual(
            mock_pipeline.call_args_list[1].kwargs["source_path_overrides"],
            {"ur_car_es": "input/downloads/ur_car_es"},
        )

    @patch("core.downloads.flow.load_download_queue_task")
    def test_default_flow_returns_empty_when_no_download_records(self, mock_load_queue):
        mock_load_queue.return_value = []

        self.assertEqual(data_download_flow.fn(), [])


if __name__ == "__main__":
    unittest.main()
