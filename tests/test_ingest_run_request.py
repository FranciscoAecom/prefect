import unittest

from core.ingest.run_request import IngestRunRequest
from core.ingest.filters import ThemeFolderFilter


class IngestRunRequestTests(unittest.TestCase):
    def test_builds_from_parameters(self):
        request = IngestRunRequest.from_parameters(
            theme_folders="localidades",
            ready_status="treatment",
            source_path_overrides={"Localidades": r"L:\base"},
        )

        self.assertEqual(request.theme_folders, ("localidades",))
        self.assertEqual(request.ready_statuses, ("treatment",))
        self.assertEqual(request.source_path_overrides, {"localidades": r"L:\base"})
        self.assertTrue(request.matches_theme_folder("localidades"))

    def test_status_flag_combinations_are_eligible_for_treatment(self):
        request = IngestRunRequest.from_parameters()

        self.assertTrue(request.is_status_eligible("download-treatment-publish"))
        self.assertFalse(request.is_status_eligible("download-publish"))
        self.assertFalse(request.is_status_eligible("download-treatment-foo"))
        self.assertFalse(request.is_status_eligible("schedule 2026-05-13 18:49"))

    def test_scheduled_request_accepts_schedule_status(self):
        request = IngestRunRequest.from_parameters(scheduled=True)

        self.assertTrue(request.is_status_eligible("schedule 2026-05-13 18:49"))
        self.assertFalse(request.is_status_eligible("treatment"))

    def test_accepts_theme_filter(self):
        request = IngestRunRequest.from_parameters(
            theme_filter=ThemeFolderFilter.from_theme_folders(["estado"])
        )

        self.assertEqual(request.theme_folders, ("estado",))

    def test_force_makes_any_status_eligible(self):
        request = IngestRunRequest.from_parameters(force=True)

        self.assertTrue(request.is_status_eligible("Complete"))

    def test_source_override_makes_theme_status_eligible(self):
        request = IngestRunRequest.from_parameters(
            source_path_overrides={"localidades": "base"}
        )

        self.assertTrue(request.is_status_eligible("Complete", "localidades"))
        self.assertFalse(request.is_status_eligible("Complete", "estado"))


if __name__ == "__main__":
    unittest.main()

