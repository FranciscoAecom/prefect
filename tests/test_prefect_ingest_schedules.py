import unittest
from datetime import datetime

from core.ingest.schedule import ScheduledTreatmentEntry
from core.prefect_support.schedules import (
    build_ingest_scheduled_treatment_schedules,
    build_scheduled_treatment_schedule,
)


class PrefectIngestScheduleTests(unittest.TestCase):
    def test_builds_prefect_schedule_from_scheduled_treatment_entry(self):
        entry = ScheduledTreatmentEntry(
            sheet_row=2,
            record_id=10,
            theme_folder="localidades",
            scheduled_for=datetime(2026, 5, 13, 18, 49),
            status="schedule 2026-05-13 18:49",
        )

        schedule = build_scheduled_treatment_schedule(entry)

        self.assertEqual(schedule.slug, "localidades-202605131849")
        self.assertEqual(
            schedule.parameters,
            {"theme_folders": ["localidades"], "scheduled": True},
        )
        self.assertIn("DTSTART:20260513T184900", schedule.rrule)
        self.assertIn("COUNT=1", schedule.rrule)

    def test_builds_prefect_schedules_from_ingest_entries(self):
        entries = [
            ScheduledTreatmentEntry(
                sheet_row=2,
                record_id=10,
                theme_folder="localidades",
                scheduled_for=datetime(2026, 5, 13, 18, 49),
                status="schedule 2026-05-13 18:49",
            )
        ]

        schedules = build_ingest_scheduled_treatment_schedules(
            load_entries=lambda **_kwargs: entries
        )

        self.assertEqual([schedule.slug for schedule in schedules], ["localidades-202605131849"])


if __name__ == "__main__":
    unittest.main()
