import unittest

from core.ingest.repository import IngestCatalogRow
from core.ingest.schedule import load_scheduled_treatment_entries


class FakeIngestRepository:
    def __init__(self, rows):
        self.rows = rows

    def iter_rows(self):
        for index, row in enumerate(self.rows, start=2):
            yield IngestCatalogRow(sheet_row=index, data=row)


class IngestScheduleTests(unittest.TestCase):
    def test_loads_scheduled_treatment_entries_from_ingest_status(self):
        repository = FakeIngestRepository(
            [
                {
                    "ID": 10,
                    "theme_folder": "Localidades",
                    "status": "schedule 2026-05-13 18:49",
                },
                {
                    "ID": 20,
                    "theme_folder": "estado",
                    "status": "treatment",
                },
            ]
        )

        entries = load_scheduled_treatment_entries(repository=repository)

        self.assertEqual(len(entries), 1)
        self.assertEqual(entries[0].sheet_row, 2)
        self.assertEqual(entries[0].record_id, 10)
        self.assertEqual(entries[0].theme_folder, "localidades")
        self.assertEqual(entries[0].scheduled_for.isoformat(), "2026-05-13T18:49:00")

    def test_filters_scheduled_entries_by_theme_folder(self):
        repository = FakeIngestRepository(
            [
                {
                    "ID": 10,
                    "theme_folder": "localidades",
                    "status": "schedule 2026-05-13 18:49",
                },
                {
                    "ID": 20,
                    "theme_folder": "estado",
                    "status": "schedule 2026-05-14 08:00",
                },
            ]
        )

        entries = load_scheduled_treatment_entries(
            repository=repository,
            theme_folders=["estado"],
        )

        self.assertEqual(len(entries), 1)
        self.assertEqual(entries[0].theme_folder, "estado")


if __name__ == "__main__":
    unittest.main()
