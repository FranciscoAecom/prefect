import logging
import threading

from core.prefect_flow import data_pipeline_flow
from core.prefect_support.admin import scheduled_run_renamer_loop
from core.prefect_support.schedules import build_ur_car_schedules


def start_scheduled_run_renamer(interval_seconds=30):
    thread = threading.Thread(
        target=scheduled_run_renamer_loop,
        kwargs={"interval_seconds": interval_seconds},
        daemon=True,
    )
    thread.start()


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(levelname)s:%(name)s:%(message)s")
    start_scheduled_run_renamer()
    data_pipeline_flow.serve(
        name="CAR - Uso Restrito",
        schedules=build_ur_car_schedules(),
        tags=["ur_car", "scheduled"],
        description=(
            "Agenda mensal das 27 bases UR CAR, uma base por dia do mes."
        ),
    )
