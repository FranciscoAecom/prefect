import argparse
import logging
import threading

from prefect.schedules import Cron

from core.flow.flows import (
    data_download_flow,
    data_treatment_flow,
    data_publish_flow,
)
from core.prefect_support.admin import scheduled_run_renamer_loop
from core.prefect_support.deployment_names import (
    AUTOS_INFRACAO_TREATMENT_DEPLOYMENT_NAME,
    AUTOS_INFRACAO_TREATMENT_QUALIFIED_DEPLOYMENT_NAME,
    DATA_DOWNLOAD_DEPLOYMENT_NAME,
    DATA_PUBLISH_DEPLOYMENT_NAME,
    UR_CAR_TREATMENT_DEPLOYMENT_NAME,
    UR_CAR_TREATMENT_QUALIFIED_DEPLOYMENT_NAME,
)
from core.prefect_support.schedules import build_daily_one_shot_ur_car_schedules


def main():
    parser = argparse.ArgumentParser(description="Serve deployments do Prefect.")
    subparsers = parser.add_subparsers(dest="deployment", required=True)

    subparsers.add_parser("data-download", help="Serve o deployment generico de download.")
    subparsers.add_parser(
        "data-publish",
        help="Serve o deployment de publicacao GeoServer/GeoNetwork.",
    )
    subparsers.add_parser(
        "ur-car-treatment",
        help="Serve o tratamento agendado de CAR Uso Restrito.",
    )
    subparsers.add_parser(
        "auto-infracoes",
        help="Serve o tratamento da base Autos de Infracao.",
    )
    subparsers.add_parser("estado", help="Serve o tratamento agendado da base Estado.")
    subparsers.add_parser(
        "localidades",
        help="Serve o tratamento da base Localidades.",
    )

    args = parser.parse_args()
    logging.basicConfig(level=logging.INFO, format="%(levelname)s:%(name)s:%(message)s")

    if args.deployment == "data-download":
        serve_data_download()
    elif args.deployment == "data-publish":
        serve_data_publish()
    elif args.deployment == "ur-car-treatment":
        serve_ur_car_treatment()
    elif args.deployment == "auto-infracoes":
        serve_autos_infracao()
    elif args.deployment == "estado":
        serve_estado()
    elif args.deployment == "localidades":
        serve_localidades()


def serve_data_download():
    data_download_flow.serve(
        name=DATA_DOWNLOAD_DEPLOYMENT_NAME,
        tags=["download", "datasets"],
        description=(
            "Baixa datasets configurados no catalogo de downloads, extrai os "
            "arquivos e opcionalmente dispara o tratamento da base baixada."
        ),
    )


def serve_data_publish():
    data_publish_flow.serve(
        name=DATA_PUBLISH_DEPLOYMENT_NAME,
        tags=["publish", "geoserver", "geonetwork"],
        description=(
            "Publica arquivos silver (.gpkg, .sld e .xml) no GeoServer e "
            "GeoNetwork. Recebe a pasta silver por parametro."
        ),
    )


def serve_ur_car_treatment():
    start_scheduled_run_renamer(
        deployment_name=UR_CAR_TREATMENT_QUALIFIED_DEPLOYMENT_NAME
    )
    data_treatment_flow.serve(
        name=UR_CAR_TREATMENT_DEPLOYMENT_NAME,
        schedules=build_daily_one_shot_ur_car_schedules(),
        tags=["ur_car", "treatment", "scheduled"],
        description=(
            "Agenda diaria das 27 bases UR CAR para tratamento, "
            "uma base por dia as 17:00."
        ),
    )


def serve_autos_infracao():
    start_scheduled_run_renamer(
        deployment_name=AUTOS_INFRACAO_TREATMENT_QUALIFIED_DEPLOYMENT_NAME,
        interval_seconds=5,
    )
    data_treatment_flow.serve(
        name=AUTOS_INFRACAO_TREATMENT_DEPLOYMENT_NAME,
        parameters={"theme_folders": ["autos_infracao"]},
        tags=["autos_infracao", "treatment"],
        description=(
            "Tratamento da base Autos de Infracao ambiental, com parametros "
            "fixos para executar somente autos_infracao."
        ),
    )


def serve_estado():
    deployment_name = "Estado"
    start_scheduled_run_renamer(
        deployment_name=f"Data Treatment/{deployment_name}",
        interval_seconds=5,
    )
    data_treatment_flow.serve(
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


def serve_localidades():
    deployment_name = "Localidades"
    start_scheduled_run_renamer(
        deployment_name=f"Data Treatment/{deployment_name}",
        interval_seconds=5,
    )
    data_treatment_flow.serve(
        name=deployment_name,
        parameters={"theme_folders": ["localidades"]},
        tags=["localidades", "treatment"],
        description="Tratamento da base Localidades do Brasil.",
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
