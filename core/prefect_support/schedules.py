from prefect.schedules import Cron


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


def build_ur_car_schedules(hour=2, minute=0, timezone="America/Sao_Paulo"):
    return [
        Cron(
            f"{minute} {hour} {day} * *",
            timezone=timezone,
            slug=theme_folder,
            parameters={"theme_folders": [theme_folder]},
        )
        for day, theme_folder in enumerate(UR_CAR_THEME_FOLDERS, start=1)
    ]


__all__ = ["UR_CAR_THEME_FOLDERS", "build_ur_car_schedules"]
