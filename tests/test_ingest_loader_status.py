import unittest
from unittest.mock import patch

import pandas as pd

from core.ingest.loader import load_treatment_records
from core.ingest.run_request import IngestRunRequest
from core.rules.catalog import RuleProfileResolution


class IngestLoaderStatusTests(unittest.TestCase):
    @patch("core.ingest.loader.resolve_input_dataset_paths_cached")
    @patch("core.ingest.loader.resolve_dataset_version_plan")
    @patch("core.ingest.loader.resolve_rule_profile_for_theme")
    @patch("core.ingest.repository.pd.read_excel")
    def test_treatment_records_accepts_treatment_flags(
        self,
        mock_read_excel,
        mock_resolve_rule_profile,
        mock_resolve_version_plan,
        mock_resolve_paths,
    ):
        mock_read_excel.return_value = pd.DataFrame(
            [
                {
                    "ID": 1,
                    "theme": "UR",
                    "theme_folder": "ur_car_ac",
                    "status": "treatment",
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
                    "status": "download-treatment",
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
                    "status": "download",
                    "path_shapefile_temp": "ur_mg",
                },
            ]
        )
        mock_resolve_rule_profile.side_effect = lambda theme_folder: RuleProfileResolution(
            theme_folder=theme_folder,
            normalized_theme_folder=theme_folder,
            project_name="car_uso_restrito",
            expected_profile_name=f"ur_car/{theme_folder}",
            profile_name=f"ur_car/{theme_folder}",
            profile_dir=None,
            profile_project_name="car_uso_restrito",
        )
        mock_resolve_paths.side_effect = lambda source_path: (f"{source_path}.gpkg",)
        mock_resolve_version_plan.return_value.silver_dir = r"L:\silver\ur_car"

        records, issues, summary = load_treatment_records()

        self.assertEqual(issues, [])
        self.assertEqual(summary["ready_candidates"], 2)
        self.assertEqual(summary["eligible_records"], 2)
        self.assertEqual(
            summary["treatment_statuses"],
            ["treatment"],
        )
        self.assertEqual(
            [record.theme_folder for record in records],
            ["ur_car_ac", "ur_car_es"],
        )
        self.assertEqual(
            [record.status for record in records],
            ["treatment", "download-treatment"],
        )
        self.assertEqual(records[0].access_constraints, "restricted")
        self.assertEqual(records[0].category_acronym, "pcd")
        self.assertEqual(records[0].citation, "SICAR")
        self.assertEqual(records[0].date, "2026-03-01")
        self.assertEqual(records[0].output_dir, r"L:\silver\ur_car")

    @patch("core.ingest.loader.resolve_input_dataset_paths_cached")
    @patch("core.ingest.loader.resolve_dataset_version_plan")
    @patch("core.ingest.loader.resolve_rule_profile_for_theme")
    @patch("core.ingest.repository.pd.read_excel")
    def test_run_request_force_processes_non_ready_status(
        self,
        mock_read_excel,
        mock_resolve_rule_profile,
        mock_resolve_version_plan,
        mock_resolve_paths,
    ):
        mock_read_excel.return_value = pd.DataFrame(
            [
                {
                    "ID": 1,
                    "theme": "Localidades",
                    "theme_folder": "localidades",
                    "status": "Complete",
                    "path_shapefile_temp": "base",
                    "access_constraints": "restricted",
                    "category_acronym": "loc",
                    "citation": "IBGE",
                    "date": "2025-11-19",
                },
            ]
        )
        mock_resolve_rule_profile.return_value = RuleProfileResolution(
            theme_folder="localidades",
            normalized_theme_folder="localidades",
            project_name="localidades",
            expected_profile_name="localidades/localidades",
            profile_name="localidades/localidades",
            profile_dir=None,
            profile_project_name="localidades",
        )
        mock_resolve_paths.return_value = ("base.gpkg",)
        mock_resolve_version_plan.return_value.silver_dir = r"L:\silver\localidades"

        records, issues, summary = load_treatment_records(
            run_request=IngestRunRequest.from_parameters(
                theme_folders=["localidades"],
                force=True,
            )
        )

        self.assertEqual(issues, [])
        self.assertEqual(len(records), 1)
        self.assertTrue(summary["force"])

    @patch("core.ingest.loader.resolve_input_dataset_paths_cached")
    @patch("core.ingest.loader.resolve_dataset_version_plan")
    @patch("core.ingest.loader.resolve_rule_profile_for_theme")
    @patch("core.ingest.repository.pd.read_excel")
    def test_run_request_source_override_makes_status_eligible(
        self,
        mock_read_excel,
        mock_resolve_rule_profile,
        mock_resolve_version_plan,
        mock_resolve_paths,
    ):
        mock_read_excel.return_value = pd.DataFrame(
            [
                {
                    "ID": 1,
                    "theme": "Localidades",
                    "theme_folder": "localidades",
                    "status": "Complete",
                    "path_shapefile_temp": "base_antiga",
                    "access_constraints": "restricted",
                    "category_acronym": "loc",
                    "citation": "IBGE",
                    "date": "2025-11-19",
                },
            ]
        )
        mock_resolve_rule_profile.return_value = RuleProfileResolution(
            theme_folder="localidades",
            normalized_theme_folder="localidades",
            project_name="localidades",
            expected_profile_name="localidades/localidades",
            profile_name="localidades/localidades",
            profile_dir=None,
            profile_project_name="localidades",
        )
        mock_resolve_paths.return_value = ("base_nova.gpkg",)
        mock_resolve_version_plan.return_value.silver_dir = r"L:\silver\localidades"

        records, issues, _summary = load_treatment_records(
            run_request=IngestRunRequest.from_parameters(
                theme_folders=["localidades"],
                source_path_overrides={"localidades": "base_nova"},
            )
        )

        self.assertEqual(issues, [])
        self.assertEqual(records[0].source_path, "base_nova")
        mock_resolve_paths.assert_called_once_with("base_nova")

    @patch("core.ingest.loader.resolve_input_dataset_paths_cached")
    @patch("core.ingest.loader.resolve_dataset_version_plan")
    @patch("core.ingest.loader.resolve_rule_profile_for_theme")
    @patch("core.ingest.repository.pd.read_excel")
    def test_missing_versioning_metadata_blocks_treatment_record(
        self,
        mock_read_excel,
        mock_resolve_rule_profile,
        mock_resolve_version_plan,
        mock_resolve_paths,
    ):
        mock_read_excel.return_value = pd.DataFrame(
            [
                {
                    "ID": 1,
                    "theme": "Localidades",
                    "theme_folder": "localidades",
                    "status": "treatment",
                    "path_shapefile_temp": "base",
                    "access_constraints": "restricted",
                    "category_acronym": "loc",
                    "citation": "",
                    "date": "2025-11-19",
                },
            ]
        )
        mock_resolve_rule_profile.return_value = RuleProfileResolution(
            theme_folder="localidades",
            normalized_theme_folder="localidades",
            project_name="localidades",
            expected_profile_name="localidades/localidades",
            profile_name="localidades/localidades",
            profile_dir=None,
            profile_project_name="localidades",
        )
        mock_resolve_paths.return_value = ("base.gpkg",)

        records, issues, summary = load_treatment_records()

        self.assertEqual(records, [])
        self.assertEqual(summary["eligible_records"], 0)
        self.assertEqual(len(issues), 1)
        self.assertEqual(issues[0].code, "versioning_metadata_incomplete")
        self.assertIn("citation", issues[0].reason)
        mock_resolve_version_plan.assert_not_called()

if __name__ == "__main__":
    unittest.main()


