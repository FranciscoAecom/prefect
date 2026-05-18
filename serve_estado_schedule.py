import logging

from prefect.schedules import Cron

from core.prefect_flow import data_pipeline_flow


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(levelname)s:%(name)s:%(message)s")
    data_pipeline_flow.serve(
        name="Estado",
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
