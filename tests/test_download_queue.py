import unittest
from unittest.mock import patch

import pandas as pd

from core.downloads.queue import load_download_queue


class DownloadQueueTests(unittest.TestCase):
    @patch("core.downloads.queue.pd.read_excel")
    def test_loads_only_download_status_with_registered_connector(self, mock_read_excel):
        mock_read_excel.return_value = pd.DataFrame(
            [
                {
                    "ID": 1,
                    "theme": "CAR APP",
                    "theme_folder": "app_car_ac",
                    "status": "download",
                    "access_constraints": "restricted",
                    "category_acronym": "pcd",
                    "citation": "SICAR",
                    "date": "2026-03-01",
                },
                {
                    "ID": 2,
                    "theme": "Autos",
                    "theme_folder": "autos_infracao",
                    "status": "download-publish",
                },
                {
                    "ID": 3,
                    "theme": "UR",
                    "theme_folder": "ur_car_es",
                    "status": "treatment",
                },
            ]
        )

        records, issues, summary = load_download_queue()

        self.assertEqual(summary["download_candidates"], 2)
        self.assertEqual(summary["eligible_records"], 1)
        self.assertEqual(summary["issues"], 1)
        self.assertEqual(records[0].dataset_key, "car_app")
        self.assertEqual(records[0].region, "AC")
        self.assertEqual(records[0].theme_folder, "app_car_ac")
        self.assertEqual(records[0].access_constraints, "restricted")
        self.assertEqual(records[0].category_acronym, "pcd")
        self.assertEqual(records[0].citation, "SICAR")
        self.assertEqual(records[0].date, "2026-03-01")
        self.assertEqual(issues[0].theme_folder, "autos_infracao")
        self.assertIn("nao existe conector/script", issues[0].reason)

    @patch("core.downloads.queue.pd.read_excel")
    def test_filters_by_theme_folder(self, mock_read_excel):
        mock_read_excel.return_value = pd.DataFrame(
            [
                {
                    "ID": 1,
                    "theme": "CAR APP",
                    "theme_folder": "app_car_ac",
                    "status": "download",
                },
                {
                    "ID": 2,
                    "theme": "UR",
                    "theme_folder": "ur_car_es",
                    "status": "download-treatment",
                },
            ]
        )

        records, issues, summary = load_download_queue(theme_folders=["ur_car_es"])

        self.assertEqual(summary["download_candidates"], 2)
        self.assertEqual(summary["eligible_records"], 1)
        self.assertEqual(issues, [])
        self.assertEqual(records[0].dataset_key, "car_uso_restrito")
        self.assertEqual(records[0].region, "ES")


if __name__ == "__main__":
    unittest.main()
