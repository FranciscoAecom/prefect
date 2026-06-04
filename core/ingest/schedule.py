from dataclasses import dataclass
from datetime import datetime

from core.ingest.filters import ThemeFolderFilter
from core.ingest.normalization import normalize_theme_folder, stringify
from core.ingest.plan import build_ingest_execution_plan
from core.ingest.repository import build_ingest_repository
from settings import INGEST_SHEET_NAME, INGEST_WORKBOOK_PATH


@dataclass(frozen=True)
class ScheduledTreatmentEntry:
    sheet_row: int
    record_id: object
    theme_folder: str
    scheduled_for: datetime
    status: str


def load_scheduled_treatment_entries(
    workbook_path=INGEST_WORKBOOK_PATH,
    sheet_name=INGEST_SHEET_NAME,
    theme_folders=None,
    repository=None,
):
    theme_filter = ThemeFolderFilter.from_theme_folders(theme_folders)
    ingest_repository = build_ingest_repository(
        workbook_path=workbook_path,
        sheet_name=sheet_name,
        repository=repository,
    )
    entries = []

    for catalog_row in ingest_repository.iter_rows():
        entry = scheduled_treatment_entry_from_row(catalog_row, theme_filter)
        if entry:
            entries.append(entry)

    return entries


def scheduled_treatment_entry_from_row(catalog_row, theme_filter=None):
    row = catalog_row.data
    theme_folder = normalize_theme_folder(row.get("theme_folder"))
    if not theme_folder:
        return None

    theme_filter = theme_filter or ThemeFolderFilter.from_theme_folders(None)
    if not theme_filter.matches_theme_folder(theme_folder):
        return None

    status = stringify(row.get("status"))
    plan = build_ingest_execution_plan(status)
    if not plan.is_scheduled_for_treatment:
        return None

    return ScheduledTreatmentEntry(
        sheet_row=catalog_row.sheet_row,
        record_id=row.get("ID"),
        theme_folder=theme_folder,
        scheduled_for=plan.scheduled_for,
        status=status,
    )


__all__ = [
    "ScheduledTreatmentEntry",
    "load_scheduled_treatment_entries",
    "scheduled_treatment_entry_from_row",
]
