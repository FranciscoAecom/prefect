import unittest

from core.ingest.plan import build_ingest_execution_plan


class IngestExecutionPlanTests(unittest.TestCase):
    def test_parses_operational_flags(self):
        plan = build_ingest_execution_plan("download-treatment-publish")

        self.assertTrue(plan.is_valid)
        self.assertTrue(plan.should_download)
        self.assertTrue(plan.should_treat)
        self.assertTrue(plan.should_publish)

    def test_reports_invalid_flags(self):
        plan = build_ingest_execution_plan("treatment-review")

        self.assertFalse(plan.is_valid)
        self.assertEqual(plan.invalid_flags, ("review",))

    def test_parses_schedule_status_for_treatment(self):
        plan = build_ingest_execution_plan("schedule 2026-05-13 18:49")

        self.assertTrue(plan.is_valid)
        self.assertTrue(plan.should_schedule)
        self.assertTrue(plan.is_scheduled_for_treatment)
        self.assertFalse(plan.should_treat)
        self.assertEqual(plan.scheduled_for.year, 2026)
        self.assertEqual(plan.scheduled_for.month, 5)
        self.assertEqual(plan.scheduled_for.day, 13)
        self.assertEqual(plan.scheduled_for.hour, 18)
        self.assertEqual(plan.scheduled_for.minute, 49)

    def test_reports_malformed_schedule_as_invalid(self):
        plan = build_ingest_execution_plan("schedule amanha")

        self.assertFalse(plan.is_valid)
        self.assertEqual(plan.invalid_flags, ("schedule amanha",))


if __name__ == "__main__":
    unittest.main()
