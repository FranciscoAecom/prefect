from datetime import date, datetime, timedelta

from prefect.schedules import Cron
from prefect.schedules import RRule

from core.prefect_support.variables import (
    get_date_variable,
    get_int_variable,
    get_str_variable,
)

DEFAULT_UR_CAR_SEQUENCE_START_DATE = date(2026, 5, 20)
DEFAULT_UR_CAR_SEQUENCE_HOUR = 17
DEFAULT_UR_CAR_SEQUENCE_MINUTE = 0
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
    "build_daily_one_shot_ur_car_schedules",
    "build_monthly_day_of_month_ur_car_schedules",
    "build_ur_car_daily_sequence_schedules",
    "build_ur_car_schedules",
    "get_ur_car_sequence_config",
]
