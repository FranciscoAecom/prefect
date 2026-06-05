import unittest
import inspect
from unittest.mock import patch

from core.flow.downloads import data_download_flow


class DownloadFlowTests(unittest.TestCase):
    def test_flow_signature_does_not_expose_manual_dataset_parameters(self):
        signature = inspect.signature(data_download_flow.fn)

        self.assertNotIn("dataset_key", signature.parameters)
        self.assertNotIn("region", signature.parameters)
        self.assertIn("theme_folders", signature.parameters)

    @patch("core.downloads.service.emit_dataset_downloaded_event_task")
    @patch("core.downloads.service.extract_download_task")
    @patch("core.downloads.service.resolve_download_version_plan_task")
    @patch("core.downloads.service.download_dataset_task")
    @patch("core.flow.downloads.load_download_queue_task")
    def test_default_flow_uses_download_queue(
        self,
        mock_load_queue,
        mock_download,
        mock_resolve_plan,
        mock_extract,
        mock_emit_event,
    ):
        mock_load_queue.return_value = [
            {
                "dataset_key": "car_app",
                "region": "AC",
                "status": "download-treatment",
                "access_constraints": "restricted",
                "category_acronym": "pcd",
                "theme_folder": "app_car_ac",
                "citation": "SICAR",
                "date": "2026-03-01",
            },
            {
                "dataset_key": "car_uso_restrito",
                "region": "ES",
                "status": "download",
                "access_constraints": "restricted",
                "category_acronym": "pcd",
                "theme_folder": "ur_car_es",
                "citation": "SICAR",
                "date": "2026-03-01",
            },
        ]
        mock_download.side_effect = [
            {"archive_path": "app.zip", "theme_folder": "app_car_ac"},
            {"archive_path": "ur.zip", "theme_folder": "ur_car_es"},
        ]
        mock_resolve_plan.side_effect = [
            {
                "version": "00",
                "temp_dir": r"L:\base\temp\restricted\pcd\app_car_ac\SICAR\20260301\00",
                "bronze_dir": r"L:\base\bronze_data\restricted\pcd\app_car_ac\SICAR\20260301\00",
                "silver_dir": r"L:\base\silver_data\restricted\pcd\app_car_ac\SICAR\20260301\00",
            },
            {
                "version": "00",
                "temp_dir": r"L:\base\temp\restricted\pcd\ur_car_es\SICAR\20260301\00",
                "bronze_dir": r"L:\base\bronze_data\restricted\pcd\ur_car_es\SICAR\20260301\00",
                "silver_dir": r"L:\base\silver_data\restricted\pcd\ur_car_es\SICAR\20260301\00",
            },
        ]
        mock_extract.side_effect = [
            {
                "archive_path": "app.zip",
                "theme_folder": "app_car_ac",
                "extract_dir": r"L:\base\temp\restricted\pcd\app_car_ac\SICAR\20260301\00\raw",
                "dataset_key": "car_app",
                "connector": "car_public_api",
                "region": "AC",
            },
            {
                "archive_path": "ur.zip",
                "theme_folder": "ur_car_es",
                "extract_dir": r"L:\base\temp\restricted\pcd\ur_car_es\SICAR\20260301\00\raw",
                "dataset_key": "car_uso_restrito",
                "connector": "car_public_api",
                "region": "ES",
            },
        ]

        result = data_download_flow.fn()

        mock_load_queue.assert_called_once_with(theme_folders=None)
        self.assertEqual(mock_download.call_count, 2)
        self.assertEqual(mock_resolve_plan.call_count, 2)
        self.assertEqual(mock_extract.call_count, 2)
        self.assertEqual(mock_emit_event.call_count, 2)
        self.assertEqual(len(result), 2)
        self.assertEqual(
            mock_extract.call_args_list[0].kwargs["extract_dir"],
            r"L:\base\temp\restricted\pcd\app_car_ac\SICAR\20260301\00\raw",
        )
        self.assertEqual(
            mock_download.call_args_list[0].kwargs["output_dir"],
            r"L:\base\temp\restricted\pcd\app_car_ac\SICAR\20260301\00\_downloads",
        )

    @patch("core.downloads.service.emit_dataset_downloaded_event_task")
    @patch("core.downloads.service.extract_download_task")
    @patch("core.downloads.service.resolve_download_version_plan_task")
    @patch("core.downloads.service.download_dataset_task")
    @patch("core.flow.downloads.load_download_queue_task")
    def test_download_flow_does_not_call_other_flows(
        self,
        mock_load_queue,
        mock_download,
        mock_resolve_plan,
        mock_extract,
        mock_emit_event,
    ):
        mock_load_queue.return_value = [
            {
                "dataset_key": "car_uso_restrito",
                "region": "AC",
                "status": "download-treatment-publish",
                "access_constraints": "restricted",
                "category_acronym": "pcd",
                "theme_folder": "ur_car_ac",
                "citation": "SICAR",
                "date": "2026-05-14",
            }
        ]
        mock_resolve_plan.return_value = {
            "version": "00",
            "temp_dir": r"L:\base\temp\restricted\pcd\ur_car_ac\SICAR\20260514\00",
            "bronze_dir": r"L:\base\bronze_data\restricted\pcd\ur_car_ac\SICAR\20260514\00",
            "silver_dir": r"L:\base\silver_data\restricted\pcd\ur_car_ac\SICAR\20260514\00",
        }
        mock_download.return_value = {
            "archive_path": "ur.zip",
            "theme_folder": "ur_car_ac",
        }
        mock_extract.return_value = {
            "archive_path": "ur.zip",
            "theme_folder": "ur_car_ac",
            "extract_dir": r"L:\base\temp\restricted\pcd\ur_car_ac\SICAR\20260514\00\raw",
            "dataset_key": "car_uso_restrito",
            "connector": "car_public_api",
            "region": "AC",
        }

        result = data_download_flow.fn(
            theme_folders=["ur_car_ac"],
            publish_after_treatment=True,
            publish_geoserver_username="admin",
            publish_geoserver_password="senha",
            publish_geonetwork_username="admin",
            publish_geonetwork_password="senha",
        )

        self.assertEqual(len(result), 1)
        self.assertEqual(mock_download.call_count, 1)
        self.assertEqual(mock_extract.call_count, 1)
        self.assertEqual(mock_emit_event.call_count, 1)

    @patch("core.flow.downloads.load_download_queue_task")
    def test_default_flow_returns_empty_when_no_download_records(self, mock_load_queue):
        mock_load_queue.return_value = []

        self.assertEqual(data_download_flow.fn(), [])


if __name__ == "__main__":
    unittest.main()
