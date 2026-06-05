import os
from dataclasses import asdict

from pydantic import Field
from prefect.blocks.core import Block
from prefect.blocks.system import Secret

from core.config.defaults import (
    DEFAULT_BRAZIL_BBOX_PATH,
    DEFAULT_CAR_PUBLIC_API_BASE,
    DEFAULT_DOWNLOAD_ARCHIVE_BASE,
    DEFAULT_DOWNLOAD_EXTRACT_BASE,
    DEFAULT_MUNICIPALITIES_BASE_PATH,
)
from core.publish.config import config_for_environment
from settings import DATA_LAKE_BASE


class DataTreatmentPaths(Block):
    """Shared filesystem paths used by data treatment."""

    data_lake_base: str = Field(description="Base folder for temp, bronze and silver data.")
    municipios_base_path: str = Field(description="Municipalities reference dataset.")
    brazil_bbox_path: str = Field(description="Brazil/coastal-zone bbox reference dataset.")
    download_extract_base: str = Field(description="Folder used to extract downloaded files.")
    download_archive_base: str = Field(description="Folder used to cache downloaded archives.")


class DataTreatmentEndpoints(Block):
    """External service endpoints used by data acquisition."""

    car_public_api_base: str = Field(description="Base URL for the public CAR API.")


class PublishEnvironment(Block):
    """GeoServer/GeoNetwork publishing configuration for one environment."""

    environment: str
    geoserver: str
    catalog: str
    workspace: str
    catalog_group: str
    catalog_category: str
    data_dictionary_base_url: str


DEFAULT_BLOCKS = {
    "paths": "geodata-workflow-paths",
    "endpoints": "geodata-workflow-endpoints",
    "publish_qas": "publish-qas",
    "publish_prod": "publish-prod",
    "geoserver_credentials": "publish-geoserver-credentials",
    "geonetwork_credentials": "publish-geonetwork-credentials",
}


def save_default_blocks(overwrite=True):
    saved = []
    skipped = []

    blocks = [
        (
            DataTreatmentPaths(
                data_lake_base=str(DATA_LAKE_BASE),
                municipios_base_path=str(DEFAULT_MUNICIPALITIES_BASE_PATH),
                brazil_bbox_path=str(DEFAULT_BRAZIL_BBOX_PATH),
                download_extract_base=str(DEFAULT_DOWNLOAD_EXTRACT_BASE),
                download_archive_base=str(DEFAULT_DOWNLOAD_ARCHIVE_BASE),
            ),
            DEFAULT_BLOCKS["paths"],
        ),
        (
            DataTreatmentEndpoints(car_public_api_base=DEFAULT_CAR_PUBLIC_API_BASE),
            DEFAULT_BLOCKS["endpoints"],
        ),
        (
            PublishEnvironment(**asdict(config_for_environment("qas"))),
            DEFAULT_BLOCKS["publish_qas"],
        ),
        (
            PublishEnvironment(**asdict(config_for_environment("prod"))),
            DEFAULT_BLOCKS["publish_prod"],
        ),
    ]

    for block, name in blocks:
        block.save(name, overwrite=overwrite)
        saved.append(name)

    secret_specs = [
        (
            DEFAULT_BLOCKS["geoserver_credentials"],
            {
                "username": os.getenv("PUBLISH_GEOSERVER_USERNAME", ""),
                "password": os.getenv("PUBLISH_GEOSERVER_PASSWORD", ""),
            },
        ),
        (
            DEFAULT_BLOCKS["geonetwork_credentials"],
            {
                "username": os.getenv("PUBLISH_GEONETWORK_USERNAME", ""),
                "password": os.getenv("PUBLISH_GEONETWORK_PASSWORD", ""),
            },
        ),
    ]
    for name, value in secret_specs:
        if not value["username"] or not value["password"]:
            skipped.append(name)
            continue
        Secret(value=value).save(name, overwrite=overwrite)
        saved.append(name)

    return {"saved": saved, "skipped": skipped}


def load_data_treatment_paths(name=DEFAULT_BLOCKS["paths"]):
    return DataTreatmentPaths.load(name)


def load_data_treatment_endpoints(name=DEFAULT_BLOCKS["endpoints"]):
    return DataTreatmentEndpoints.load(name)


def load_publish_environment(environment="qas"):
    key = "publish_prod" if str(environment).lower() == "prod" else "publish_qas"
    return PublishEnvironment.load(DEFAULT_BLOCKS[key])


def block_path(name, block_type_slug):
    return f"{block_type_slug}/{name}"


__all__ = [
    "DEFAULT_BLOCKS",
    "DataTreatmentEndpoints",
    "DataTreatmentPaths",
    "PublishEnvironment",
    "block_path",
    "load_data_treatment_endpoints",
    "load_data_treatment_paths",
    "load_publish_environment",
    "save_default_blocks",
]
