from dataclasses import dataclass
from getpass import getpass
import os


@dataclass(frozen=True)
class PublishConfig:
    geoserver: str = "https://gisqas.iocasta.com.br/geoserver"
    catalog: str = "https://catalogqas.iocasta.com.br"
    workspace: str = "gold"
    catalog_group: str = "2"
    catalog_category: str = "2"
    data_dictionary_base_url: str = (
        "https://etlapiqas.iocasta.com.br/get_geonetwork_data_dict"
    )
    environment: str = "qas"


@dataclass(frozen=True)
class PublishCredentials:
    geoserver_username: str
    geoserver_password: str
    catalog_username: str
    catalog_password: str


def load_publish_credentials(
    same_credential_for_catalog=True,
    allow_prompt=True,
):
    geo_user = os.getenv("PUBLISH_GEOSERVER_USERNAME", "")
    geo_password = os.getenv("PUBLISH_GEOSERVER_PASSWORD", "")
    catalog_user = os.getenv("PUBLISH_GEONETWORK_USERNAME", "")
    catalog_password = os.getenv("PUBLISH_GEONETWORK_PASSWORD", "")

    if not allow_prompt and (not geo_user or not geo_password):
        geo_user = geo_user or "DRYRUN"
        geo_password = geo_password or "DRYRUN"

    if allow_prompt and (not geo_user or not geo_password):
        geo_user = geo_user or input("Usuario GeoServer: ")
        geo_password = geo_password or getpass("Senha GeoServer: ")

    if same_credential_for_catalog:
        catalog_user = catalog_user or geo_user
        catalog_password = catalog_password or geo_password
    elif not allow_prompt and (not catalog_user or not catalog_password):
        catalog_user = catalog_user or "DRYRUN"
        catalog_password = catalog_password or "DRYRUN"
    elif allow_prompt and (not catalog_user or not catalog_password):
        catalog_user = catalog_user or input("Usuario GeoNetwork: ")
        catalog_password = catalog_password or getpass("Senha GeoNetwork: ")

    if not geo_user or not geo_password:
        raise ValueError(
            "Credenciais do GeoServer nao informadas. Configure "
            "PUBLISH_GEOSERVER_USERNAME e PUBLISH_GEOSERVER_PASSWORD."
        )
    if not catalog_user or not catalog_password:
        raise ValueError(
            "Credenciais do GeoNetwork nao informadas. Configure "
            "PUBLISH_GEONETWORK_USERNAME e PUBLISH_GEONETWORK_PASSWORD."
        )

    return PublishCredentials(
        geoserver_username=geo_user,
        geoserver_password=geo_password,
        catalog_username=catalog_user,
        catalog_password=catalog_password,
    )


def config_for_environment(environment="qas", **overrides):
    defaults = {
        "qas": PublishConfig(),
        "prod": PublishConfig(
            geoserver="https://gis.iocasta.com.br/geoserver",
            catalog="https://catalog.iocasta.com.br",
            data_dictionary_base_url=(
                "https://etlapi.iocasta.com.br/get_geonetwork_data_dict"
            ),
            environment="prod",
        ),
    }
    config = defaults.get((environment or "qas").lower())
    if config is None:
        raise ValueError(f"Ambiente de publicacao nao suportado: {environment}")

    values = config.__dict__.copy()
    values.update({key: value for key, value in overrides.items() if value is not None})
    return PublishConfig(**values)
