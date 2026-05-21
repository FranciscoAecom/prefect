import unittest
from unittest.mock import patch

import pandas as pd

from core.ingest.loader import load_processing_queue


class IngestLoaderStatusTests(unittest.TestCase):
    @patch("core.ingest.loader.resolve_input_dataset_paths_cached")
    @patch("core.ingest.loader.resolve_dataset_version_plan")
    @patch("core.ingest.loader.get_rule_profile_project_name")
    @patch("core.ingest.loader.find_rule_profile_by_theme_folder")
    @patch("core.ingest.loader.pd.read_excel")
    def test_processing_queue_accepts_waiting_update_and_reprocessing(
        self,
        mock_read_excel,
        mock_find_rule_profile,
        mock_get_rule_project,
        mock_resolve_version_plan,
        mock_resolve_paths,
    ):
        mock_read_excel.return_value = pd.DataFrame(
            [
                {
                    "ID": 1,
                    "theme": "UR",
                    "theme_folder": "ur_car_ac",
                    "status": "Waiting Update",
                    "path_shapefile_temp": "ur_ac",
                    "access_constraints": "restricted",
                    "category_acronym": "pcd",
                    "citation": "SICAR",
                    "date": "2026-03-01",
                },
                {
                    "ID": 2,
                    "theme": "UR",
                    "theme_folder": "ur_car_es",
                    "status": "Reprocessing",
                    "path_shapefile_temp": "ur_es",
                    "access_constraints": "restricted",
                    "category_acronym": "pcd",
                    "citation": "SICAR",
                    "date": "2026-03-01",
                },
                {
                    "ID": 3,
                    "theme": "UR",
                    "theme_folder": "ur_car_mg",
                    "status": "Download",
                    "path_shapefile_temp": "ur_mg",
                },
            ]
        )
        mock_find_rule_profile.side_effect = lambda theme_folder: f"ur_car/{theme_folder}"
        mock_get_rule_project.return_value = "ur_car"
        mock_resolve_paths.side_effect = lambda source_path: (f"{source_path}.gpkg",)
        mock_resolve_version_plan.return_value.silver_dir = r"L:\silver\ur_car"

        records, issues, summary = load_processing_queue()

        self.assertEqual(issues, [])
        self.assertEqual(summary["ready_candidates"], 2)
        self.assertEqual(summary["eligible_records"], 2)
        self.assertEqual(
            summary["processing_statuses"],
            ["Waiting Update", "Reprocessing"],
        )
        self.assertEqual(
            [record.theme_folder for record in records],
            ["ur_car_ac", "ur_car_es"],
        )
        self.assertEqual(
            [record.status for record in records],
            ["Waiting Update", "Reprocessing"],
        )
        self.assertEqual(records[0].access_constraints, "restricted")
        self.assertEqual(records[0].category_acronym, "pcd")
        self.assertEqual(records[0].citation, "SICAR")
        self.assertEqual(records[0].date, "2026-03-01")
        self.assertEqual(records[0].output_dir, r"L:\silver\ur_car")


if __name__ == "__main__":
    unittest.main()
