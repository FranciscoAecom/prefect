import logging
import threading

from prefect.schedules import Cron

from core.prefect_flow import data_pipeline_flow
from core.prefect_support.admin import scheduled_run_renamer_loop


DEPLOYMENT_NAME = "Estado"
QUALIFIED_DEPLOYMENT_NAME = f"Data Pipeline/{DEPLOYMENT_NAME}"


def start_scheduled_run_renamer(interval_seconds=30):
    thread = threading.Thread(
        target=scheduled_run_renamer_loop,
        kwargs={
            "interval_seconds": interval_seconds,
            "deployment_name": QUALIFIED_DEPLOYMENT_NAME,
        },
        daemon=True,
    )
    thread.start()


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(levelname)s:%(name)s:%(message)s")
    start_scheduled_run_renamer()
    data_pipeline_flow.serve(
        name=DEPLOYMENT_NAME,
        schedules=[
            Cron(
                "0 2 * * *",
                timezone="America/Sao_Paulo",
                slug="estado",
                parameters={"theme_folders": ["estado"]},
            )
        ],
        tags=["estado", "scheduled"],
        description="Agenda da base de estados.",
    )
