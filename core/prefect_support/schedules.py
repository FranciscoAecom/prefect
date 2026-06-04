from dataclasses import dataclass
from datetime import date, datetime, timedelta

from prefect.schedules import Cron
from prefect.schedules import RRule

from core.ingest.filters import ThemeFolderFilter
from core.ingest.normalization import normalize_theme_folder, stringify
from core.ingest.plan import build_ingest_execution_plan
from core.ingest.repository import build_ingest_repository
from core.prefect_support.variables import (
    get_date_variable,
    get_int_variable,
    get_str_variable,
)
from settings import INGEST_SHEET_NAME, INGEST_WORKBOOK_PATH

DEFAULT_UR_CAR_SEQUENCE_START_DATE = date(2026, 5, 20)
DEFAULT_UR_CAR_SEQUENCE_HOUR = 17
DEFAULT_UR_CAR_SEQUENCE_MINUTE = 30
DEFAULT_UR_CAR_SEQUENCE_TIMEZONE = "America/Sao_Paulo"

UR_CAR_SEQUENCE_START_DATE = DEFAULT_UR_CAR_SEQUENCE_START_DATE
UR_CAR_SEQUENCE_HOUR = DEFAULT_UR_CAR_SEQUENCE_HOUR
UR_CAR_SEQUENCE_MINUTE = DEFAULT_UR_CAR_SEQUENCE_MINUTE
UR_CAR_SEQUENCE_TIMEZONE = DEFAULT_UR_CAR_SEQUENCE_TIMEZONE

UR_CAR_THEME_FOLDERS = [
    "ur_car_ac",
    "ur_car_al",
    "ur_car_am",
    "ur_car_ap",
    "ur_car_ba",
    "ur_car_ce",
    "ur_car_df",
    "ur_car_es",
    "ur_car_go",
    "ur_car_ma",
    "ur_car_mg",
    "ur_car_ms",
    "ur_car_mt",
    "ur_car_pa",
    "ur_car_pb",
    "ur_car_pe",
    "ur_car_pi",
    "ur_car_pr",
    "ur_car_rj",
    "ur_car_rn",
    "ur_car_ro",
    "ur_car_rr",
    "ur_car_rs",
    "ur_car_sc",
    "ur_car_se",
    "ur_car_sp",
    "ur_car_to",
]


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
        row = catalog_row.data
        theme_folder = normalize_theme_folder(row.get("theme_folder"))
        if not theme_folder or not theme_filter.matches_theme_folder(theme_folder):
            continue

        status = stringify(row.get("status"))
        plan = build_ingest_execution_plan(status)
        if not plan.is_scheduled_for_treatment:
            continue

        entries.append(
            ScheduledTreatmentEntry(
                sheet_row=catalog_row.sheet_row,
                record_id=row.get("ID"),
                theme_folder=theme_folder,
                scheduled_for=plan.scheduled_for,
                status=status,
            )
        )

    return entries


def build_ingest_scheduled_treatment_schedules(
    workbook_path=INGEST_WORKBOOK_PATH,
    sheet_name=INGEST_SHEET_NAME,
    theme_folders=None,
    timezone=UR_CAR_SEQUENCE_TIMEZONE,
    repository=None,
):
    return [
        RRule(
            _single_run_rrule_datetime(entry.scheduled_for),
            timezone=timezone,
            slug=f"{entry.theme_folder}-{entry.scheduled_for:%Y%m%d%H%M}",
            parameters={
                "theme_folders": [entry.theme_folder],
                "scheduled": True,
            },
        )
        for entry in load_scheduled_treatment_entries(
            workbook_path=workbook_path,
            sheet_name=sheet_name,
            theme_folders=theme_folders,
            repository=repository,
        )
    ]


def build_monthly_day_of_month_ur_car_schedules(
    hour=2,
    minute=0,
    timezone=UR_CAR_SEQUENCE_TIMEZONE,
):
    return [
        Cron(
            f"{minute} {hour} {day} * *",
            timezone=timezone,
            slug=theme_folder,
            parameters={"theme_folders": [theme_folder]},
        )
        for day, theme_folder in enumerate(UR_CAR_THEME_FOLDERS, start=1)
    ]


def build_daily_one_shot_ur_car_schedules(
    start_date=None,
    hour=None,
    minute=None,
    timezone=None,
):
    start_date, hour, minute, timezone = get_ur_car_sequence_config(
        start_date=start_date,
        hour=hour,
        minute=minute,
        timezone=timezone,
    )
    return [
        RRule(
            _single_run_rrule(start_date + timedelta(days=index), hour, minute),
            timezone=timezone,
            slug=theme_folder,
            parameters={"theme_folders": [theme_folder]},
        )
        for index, theme_folder in enumerate(UR_CAR_THEME_FOLDERS)
    ]


def _single_run_rrule(scheduled_date, hour, minute):
    scheduled_at = datetime(
        scheduled_date.year,
        scheduled_date.month,
        scheduled_date.day,
        hour,
        minute,
    )
    return _single_run_rrule_datetime(scheduled_at)


def _single_run_rrule_datetime(scheduled_at):
    return f"DTSTART:{scheduled_at:%Y%m%dT%H%M%S}\nRRULE:FREQ=DAILY;COUNT=1"


def get_ur_car_sequence_config(
    start_date=None,
    hour=None,
    minute=None,
    timezone=None,
):
    return (
        start_date
        or get_date_variable(
            "ur_car_sequence_start_date",
            DEFAULT_UR_CAR_SEQUENCE_START_DATE,
        ),
        hour
        if hour is not None
        else get_int_variable("ur_car_sequence_hour", DEFAULT_UR_CAR_SEQUENCE_HOUR),
        minute
        if minute is not None
        else get_int_variable(
            "ur_car_sequence_minute",
            DEFAULT_UR_CAR_SEQUENCE_MINUTE,
        ),
        timezone
        or get_str_variable(
            "ur_car_sequence_timezone",
            DEFAULT_UR_CAR_SEQUENCE_TIMEZONE,
        ),
    )


build_ur_car_schedules = build_monthly_day_of_month_ur_car_schedules
build_ur_car_daily_sequence_schedules = build_daily_one_shot_ur_car_schedules


__all__ = [
    "DEFAULT_UR_CAR_SEQUENCE_HOUR",
    "DEFAULT_UR_CAR_SEQUENCE_MINUTE",
    "DEFAULT_UR_CAR_SEQUENCE_START_DATE",
    "DEFAULT_UR_CAR_SEQUENCE_TIMEZONE",
    "UR_CAR_SEQUENCE_HOUR",
    "UR_CAR_SEQUENCE_MINUTE",
    "UR_CAR_SEQUENCE_START_DATE",
    "UR_CAR_SEQUENCE_TIMEZONE",
    "UR_CAR_THEME_FOLDERS",
    "ScheduledTreatmentEntry",
    "build_ingest_scheduled_treatment_schedules",
    "build_daily_one_shot_ur_car_schedules",
    "build_monthly_day_of_month_ur_car_schedules",
    "build_ur_car_daily_sequence_schedules",
    "build_ur_car_schedules",
    "get_ur_car_sequence_config",
    "load_scheduled_treatment_entries",
]
