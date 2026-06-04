import unittest

from core.ingest.eligibility import (
    REASON_FORCE_ENABLED,
    REASON_INVALID_STATUS_FLAGS,
    REASON_MISSING_SOURCE_PATH,
    REASON_SOURCE_PATH_OVERRIDDEN,
    REASON_STATUS_NOT_ALLOWED,
    REASON_THEME_NOT_REQUESTED,
    REASON_ZIP_SOURCE_PATH,
    evaluate_ingest_row,
)
from core.ingest.run_request import IngestRunRequest


class IngestEligibilityTests(unittest.TestCase):
    def test_allows_ready_row_for_requested_theme(self):
        eligibility = evaluate_ingest_row(
            {
                "theme_folder": "localidades",
                "status": "treatment",
                "path_shapefile_temp": r"L:\base.gpkg",
            },
            IngestRunRequest.from_parameters(theme_folders=["localidades"]),
        )

        self.assertTrue(eligibility.status_allowed)
        self.assertTrue(eligibility.theme_requested)
        self.assertTrue(eligibility.selected_by_request)
        self.assertTrue(eligibility.can_attempt_treatment)
        self.assertEqual(eligibility.blocking_reasons, ())

    def test_reports_status_and_theme_blocks(self):
        eligibility = evaluate_ingest_row(
            {
                "theme_folder": "estado",
                "status": "Complete",
                "path_shapefile_temp": r"L:\base.gpkg",
            },
            IngestRunRequest.from_parameters(theme_folders=["localidades"]),
        )

        self.assertFalse(eligibility.selected_by_request)
        self.assertIn(REASON_INVALID_STATUS_FLAGS, eligibility.blocking_reasons)
        self.assertIn(REASON_THEME_NOT_REQUESTED, eligibility.blocking_reasons)

    def test_reports_invalid_status_flags(self):
        eligibility = evaluate_ingest_row(
            {
                "theme_folder": "localidades",
                "status": "treatment-foo",
                "path_shapefile_temp": r"L:\base.gpkg",
            },
            IngestRunRequest.from_parameters(theme_folders=["localidades"]),
        )

        self.assertFalse(eligibility.status_allowed)
        self.assertEqual(eligibility.invalid_status_flags, ("foo",))
        self.assertIn(REASON_INVALID_STATUS_FLAGS, eligibility.blocking_reasons)

    def test_force_allows_status_and_keeps_request_reason(self):
        eligibility = evaluate_ingest_row(
            {
                "theme_folder": "localidades",
                "status": "Complete",
                "path_shapefile_temp": r"L:\base.gpkg",
            },
            IngestRunRequest.from_parameters(
                theme_folders=["localidades"],
                force=True,
            ),
        )

        self.assertTrue(eligibility.status_allowed)
        self.assertIn(REASON_FORCE_ENABLED, eligibility.request_reasons)
        self.assertNotIn(REASON_STATUS_NOT_ALLOWED, eligibility.blocking_reasons)

    def test_source_override_replaces_path_and_allows_status(self):
        eligibility = evaluate_ingest_row(
            {
                "theme_folder": "localidades",
                "status": "Complete",
                "path_shapefile_temp": r"L:\old.gpkg",
            },
            IngestRunRequest.from_parameters(
                theme_folders=["localidades"],
                source_path_overrides={"localidades": r"L:\new.gpkg"},
            ),
        )

        self.assertEqual(eligibility.source_path, r"L:\new.gpkg")
        self.assertTrue(eligibility.status_allowed)
        self.assertIn(REASON_SOURCE_PATH_OVERRIDDEN, eligibility.request_reasons)

    def test_reports_missing_source_path(self):
        eligibility = evaluate_ingest_row(
            {"theme_folder": "localidades", "status": "treatment"},
            IngestRunRequest.from_parameters(theme_folders=["localidades"]),
        )

        self.assertFalse(eligibility.can_attempt_treatment)
        self.assertIn(REASON_MISSING_SOURCE_PATH, eligibility.blocking_reasons)

    def test_reports_zip_source_path(self):
        eligibility = evaluate_ingest_row(
            {
                "theme_folder": "localidades",
                "status": "treatment",
                "path_shapefile_temp": r"L:\base.zip",
            },
            IngestRunRequest.from_parameters(theme_folders=["localidades"]),
        )

        self.assertFalse(eligibility.can_attempt_treatment)
        self.assertIn(REASON_ZIP_SOURCE_PATH, eligibility.blocking_reasons)


if __name__ == "__main__":
    unittest.main()

