import argparse
import logging
import threading

from prefect.schedules import Cron

from core.downloads.flow import data_download_flow
from core.prefect_flow import data_pipeline_flow
from core.prefect_support.admin import scheduled_run_renamer_loop
from core.prefect_support.deployment_names import (
    AUTO_INFRACOES_PROCESSING_DEPLOYMENT_NAME,
    AUTO_INFRACOES_PROCESSING_QUALIFIED_DEPLOYMENT_NAME,
    DATA_DOWNLOAD_DEPLOYMENT_NAME,
    UR_CAR_PROCESSING_DEPLOYMENT_NAME,
    UR_CAR_PROCESSING_QUALIFIED_DEPLOYMENT_NAME,
)
from core.prefect_support.schedules import build_daily_one_shot_ur_car_schedules


def main():
    parser = argparse.ArgumentParser(description="Serve deployments do Prefect.")
    subparsers = parser.add_subparsers(dest="deployment", required=True)

    subparsers.add_parser("data-download", help="Serve o deployment generico de download.")
    subparsers.add_parser(
        "ur-car-processing",
        help="Serve o tratamento agendado de CAR Uso Restrito.",
    )
    subparsers.add_parser(
        "auto-infracoes",
        help="Serve o tratamento da base Autos de Infracao.",
    )
    subparsers.add_parser("estado", help="Serve o tratamento agendado da base Estado.")

    args = parser.parse_args()
    logging.basicConfig(level=logging.INFO, format="%(levelname)s:%(name)s:%(message)s")

    if args.deployment == "data-download":
        serve_data_download()
    elif args.deployment == "ur-car-processing":
        serve_ur_car_processing()
    elif args.deployment == "auto-infracoes":
        serve_auto_infracoes()
    elif args.deployment == "estado":
        serve_estado()


def serve_data_download():
    data_download_flow.serve(
        name=DATA_DOWNLOAD_DEPLOYMENT_NAME,
        tags=["download", "datasets"],
        description=(
            "Baixa datasets configurados no catalogo de downloads, extrai os "
            "arquivos e opcionalmente dispara o tratamento da base baixada."
        ),
    )


def serve_ur_car_processing():
    start_scheduled_run_renamer(
        deployment_name=UR_CAR_PROCESSING_QUALIFIED_DEPLOYMENT_NAME
    )
    data_pipeline_flow.serve(
        name=UR_CAR_PROCESSING_DEPLOYMENT_NAME,
        schedules=build_daily_one_shot_ur_car_schedules(),
        tags=["ur_car", "processing", "scheduled"],
        description=(
            "Agenda diaria das 27 bases UR CAR para tratamento, "
            "uma base por dia as 17:00."
        ),
    )


def serve_auto_infracoes():
    start_scheduled_run_renamer(
        deployment_name=AUTO_INFRACOES_PROCESSING_QUALIFIED_DEPLOYMENT_NAME,
        interval_seconds=5,
    )
    data_pipeline_flow.serve(
        name=AUTO_INFRACOES_PROCESSING_DEPLOYMENT_NAME,
        parameters={"theme_folders": ["autos_infracao"]},
        tags=["auto_infracoes", "autos_infracao", "processing"],
        description=(
            "Tratamento da base Autos de Infracao ambiental, com parametros "
            "fixos para executar somente autos_infracao."
        ),
    )


def serve_estado():
    deployment_name = "Estado"
    start_scheduled_run_renamer(
        deployment_name=f"Data Pipeline/{deployment_name}",
        interval_seconds=5,
    )
    data_pipeline_flow.serve(
        name=deployment_name,
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


def start_scheduled_run_renamer(deployment_name, interval_seconds=30):
    thread = threading.Thread(
        target=scheduled_run_renamer_loop,
        kwargs={
            "interval_seconds": interval_seconds,
            "deployment_name": deployment_name,
        },
        daemon=True,
    )
    thread.start()


if __name__ == "__main__":
    main()
