import unittest

from core.ingest.status_flags import (
    parse_ingest_status,
    parse_status_flags,
    parse_status_schedule,
)


class IngestStatusFlagsTests(unittest.TestCase):
    def test_parses_combined_operational_flags_once(self):
        status = parse_ingest_status("download-treatment-publish")

        self.assertTrue(status.is_valid)
        self.assertEqual(status.flags, frozenset({"download", "treatment", "publish"}))
        self.assertTrue(status.has_download)
        self.assertTrue(status.has_treatment)
        self.assertTrue(status.has_publish)
        self.assertFalse(status.has_schedule)

    def test_parses_schedule_status(self):
        status = parse_ingest_status("schedule 2026-05-13 18:49")

        self.assertTrue(status.is_valid)
        self.assertEqual(status.flags, frozenset({"schedule"}))
        self.assertTrue(status.is_scheduled_for_treatment)
        self.assertEqual(status.scheduled_for.isoformat(), "2026-05-13T18:49:00")

    def test_keeps_backward_compatible_helpers(self):
        self.assertEqual(
            parse_status_flags("download-treatment"),
            frozenset({"download", "treatment"}),
        )
        self.assertEqual(
            parse_status_schedule("schedule 2026-05-13 18:49").isoformat(),
            "2026-05-13T18:49:00",
        )


if __name__ == "__main__":
    unittest.main()
