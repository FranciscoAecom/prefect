import argparse
import logging
import threading

from core.flow.flows import (
    data_download_flow,
    data_treatment_flow,
    data_publish_flow,
)
from core.prefect_support.admin import scheduled_run_renamer_loop
from core.prefect_support.deployment_names import (
    DATA_DOWNLOAD_DEPLOYMENT_NAME,
    DATA_PUBLISH_DEPLOYMENT_NAME,
    SCHEDULED_TREATMENT_DEPLOYMENT_NAME,
    SCHEDULED_TREATMENT_QUALIFIED_DEPLOYMENT_NAME,
)
from core.prefect_support.schedules import (
    build_treatment_schedules,
)


def main():
    parser = argparse.ArgumentParser(description="Serve deployments do Prefect.")
    subparsers = parser.add_subparsers(dest="deployment", required=True)

    subparsers.add_parser("data-download", help="Serve o deployment generico de download.")
    subparsers.add_parser(
        "data-publish",
        help="Serve o deployment de publicacao GeoServer/GeoNetwork.",
    )
    subparsers.add_parser(
        "scheduled-treatment",
        help="Serve o tratamento agendado pelas linhas schedule da ingest.",
    )

    args = parser.parse_args()
    logging.basicConfig(level=logging.INFO, format="%(levelname)s:%(name)s:%(message)s")

    if args.deployment == "data-download":
        serve_data_download()
    elif args.deployment == "data-publish":
        serve_data_publish()
    elif args.deployment == "scheduled-treatment":
        serve_scheduled_treatment()


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


def serve_scheduled_treatment():
    start_scheduled_run_renamer(
        deployment_name=SCHEDULED_TREATMENT_QUALIFIED_DEPLOYMENT_NAME,
        interval_seconds=5,
    )
    data_treatment_flow.serve(
        name=SCHEDULED_TREATMENT_DEPLOYMENT_NAME,
        schedules=build_treatment_schedules(),
        tags=["treatment", "scheduled", "ingest"],
        description=(
            "Tratamento agendado a partir do status da planilha ingest no "
            "formato: schedule YYYY-MM-DD HH:MM."
        ),
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
