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


if __name__ == "__main__":
    unittest.main()
