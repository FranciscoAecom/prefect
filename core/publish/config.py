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


@dataclass(frozen=True)
class PublishOptions:
    environment: str = "qas"
    workspace: str = "gold"
    geoserver: str | None = None
    catalog: str | None = None
    catalog_group: str = "2"
    catalog_category: str = "2"
    data_dictionary_base_url: str | None = None
    same_credential_for_catalog: bool = True
    geoserver_username: str | None = None
    geoserver_password: str | None = None
    geonetwork_username: str | None = None
    geonetwork_password: str | None = None
    dry_run: bool = False
    skip_geoserver: bool = False
    skip_data: bool = False
    skip_catalog: bool = False

    def build_config(self):
        return config_for_environment(
            self.environment,
            geoserver=self.geoserver,
            catalog=self.catalog,
            workspace=self.workspace,
            catalog_group=self.catalog_group,
            catalog_category=self.catalog_category,
            data_dictionary_base_url=self.data_dictionary_base_url,
        )

    def load_credentials(self, allow_prompt=False):
        return load_publish_credentials(
            same_credential_for_catalog=self.same_credential_for_catalog,
            allow_prompt=allow_prompt,
            geoserver_username=self.geoserver_username,
            geoserver_password=self.geoserver_password,
            geonetwork_username=self.geonetwork_username,
            geonetwork_password=self.geonetwork_password,
        )

    def execution_kwargs(self):
        return {
            "dry_run": self.dry_run,
            "skip_geoserver": self.skip_geoserver,
            "skip_data": self.skip_data,
            "skip_catalog": self.skip_catalog,
        }

    def task_kwargs(self):
        return {
            "environment": self.environment,
            "workspace": self.workspace,
            "geoserver": self.geoserver,
            "catalog": self.catalog,
            "catalog_group": self.catalog_group,
            "catalog_category": self.catalog_category,
            "data_dictionary_base_url": self.data_dictionary_base_url,
            "same_credential_for_catalog": self.same_credential_for_catalog,
            "geoserver_username": self.geoserver_username,
            "geoserver_password": self.geoserver_password,
            "geonetwork_username": self.geonetwork_username,
            "geonetwork_password": self.geonetwork_password,
            **self.execution_kwargs(),
        }


def load_publish_credentials(
    same_credential_for_catalog=True,
    allow_prompt=True,
    geoserver_username=None,
    geoserver_password=None,
    geonetwork_username=None,
    geonetwork_password=None,
):
    geo_user = geoserver_username or os.getenv("PUBLISH_GEOSERVER_USERNAME", "")
    geo_password = geoserver_password or os.getenv("PUBLISH_GEOSERVER_PASSWORD", "")
    catalog_user = geonetwork_username or os.getenv("PUBLISH_GEONETWORK_USERNAME", "")
    catalog_password = geonetwork_password or os.getenv("PUBLISH_GEONETWORK_PASSWORD", "")

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
