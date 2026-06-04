from prefect.schedules import RRule

from core.ingest.schedule import load_scheduled_treatment_entries
from settings import INGEST_SHEET_NAME, INGEST_WORKBOOK_PATH

DEFAULT_SCHEDULE_TIMEZONE = "America/Sao_Paulo"


def build_ingest_scheduled_treatment_schedules(
    workbook_path=INGEST_WORKBOOK_PATH,
    sheet_name=INGEST_SHEET_NAME,
    theme_folders=None,
    timezone=DEFAULT_SCHEDULE_TIMEZONE,
    repository=None,
    load_entries=load_scheduled_treatment_entries,
):
    return [
        build_scheduled_treatment_schedule(entry, timezone=timezone)
        for entry in load_entries(
            workbook_path=workbook_path,
            sheet_name=sheet_name,
            theme_folders=theme_folders,
            repository=repository,
        )
    ]


def build_scheduled_treatment_schedule(entry, timezone=DEFAULT_SCHEDULE_TIMEZONE):
    return RRule(
        single_run_rrule(entry.scheduled_for),
        timezone=timezone,
        slug=scheduled_treatment_slug(entry),
        parameters={
            "theme_folders": [entry.theme_folder],
            "scheduled": True,
        },
    )


def scheduled_treatment_slug(entry):
    return f"{entry.theme_folder}-{entry.scheduled_for:%Y%m%d%H%M}"


def single_run_rrule(scheduled_at):
    return f"DTSTART:{scheduled_at:%Y%m%dT%H%M%S}\nRRULE:FREQ=DAILY;COUNT=1"


__all__ = [
    "DEFAULT_SCHEDULE_TIMEZONE",
    "build_ingest_scheduled_treatment_schedules",
    "build_scheduled_treatment_schedule",
    "scheduled_treatment_slug",
    "single_run_rrule",
]
