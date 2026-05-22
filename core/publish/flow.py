from prefect import flow, task

from core.publish.config import config_for_environment, load_publish_credentials
from core.publish.geonetwork import import_metadata_to_geonetwork
from core.publish.geoserver import publish_to_geoserver
from core.publish.metadata import discover_publish_items
from core.utils import log


@task(name="Descobrir arquivos para publicacao", log_prints=True)
def discover_publish_items_task(folder, store=None, layer=None, style=None, layer_title=None):
    items = discover_publish_items(
        folder,
        store=store,
        layer=layer,
        style=style,
        layer_title=layer_title,
    )
    log(f"Itens de publicacao encontrados: {len(items)}")
    for item in items:
        log(f"  Dados: {item.data_path}")
        log(f"  SLD: {item.sld_path}")
        log(f"  XML: {item.xml_path}")
    return items


@task(name="Publicar item GeoServer GeoNetwork", log_prints=True)
def publish_item_task(
    item,
    environment="qas",
    geoserver=None,
    catalog=None,
    workspace=None,
    catalog_group=None,
    catalog_category=None,
    data_dictionary_base_url=None,
    same_credential_for_catalog=True,
    geoserver_username=None,
    geoserver_password=None,
    geonetwork_username=None,
    geonetwork_password=None,
    dry_run=False,
    skip_geoserver=False,
    skip_data=False,
    skip_catalog=False,
):
    config = config_for_environment(
        environment,
        geoserver=geoserver,
        catalog=catalog,
        workspace=workspace,
        catalog_group=catalog_group,
        catalog_category=catalog_category,
        data_dictionary_base_url=data_dictionary_base_url,
    )
    credentials = load_publish_credentials(
        same_credential_for_catalog=same_credential_for_catalog,
        allow_prompt=False,
        geoserver_username=geoserver_username,
        geoserver_password=geoserver_password,
        geonetwork_username=geonetwork_username,
        geonetwork_password=geonetwork_password,
    )

    log(f"Publicando layer: {item.layer}")
    log(f"Ambiente: {config.environment}")
    log(f"GeoServer: {config.geoserver}")
    log(f"GeoNetwork: {config.catalog}")
    log(f"Workspace: {config.workspace}")

    if skip_geoserver:
        log("Etapas do GeoServer ignoradas por parametro.")
    else:
        publish_to_geoserver(
            item,
            config,
            credentials,
            dry_run=dry_run,
            skip_data=skip_data,
        )

    if skip_catalog:
        log("Importacao GeoNetwork ignorada por parametro.")
    else:
        import_metadata_to_geonetwork(item, config, credentials, dry_run=dry_run)

    log(f"Publicacao concluida: {item.layer}")


@flow(name="Data Publish", log_prints=True)
def data_publish_flow(
    folder,
    environment="qas",
    workspace="gold",
    store=None,
    layer=None,
    style=None,
    layer_title=None,
    geoserver=None,
    catalog=None,
    catalog_group="2",
    catalog_category="2",
    data_dictionary_base_url=None,
    same_credential_for_catalog=True,
    geoserver_username=None,
    geoserver_password=None,
    geonetwork_username=None,
    geonetwork_password=None,
    dry_run=False,
    skip_geoserver=False,
    skip_data=False,
    skip_catalog=False,
):
    items = discover_publish_items_task(
        folder,
        store=store,
        layer=layer,
        style=style,
        layer_title=layer_title,
    )
    for item in items:
        publish_item_task(
            item,
            environment=environment,
            geoserver=geoserver,
            catalog=catalog,
            workspace=workspace,
            catalog_group=catalog_group,
            catalog_category=catalog_category,
            data_dictionary_base_url=data_dictionary_base_url,
            same_credential_for_catalog=same_credential_for_catalog,
            geoserver_username=geoserver_username,
            geoserver_password=geoserver_password,
            geonetwork_username=geonetwork_username,
            geonetwork_password=geonetwork_password,
            dry_run=dry_run,
            skip_geoserver=skip_geoserver,
            skip_data=skip_data,
            skip_catalog=skip_catalog,
        )


__all__ = ["data_publish_flow"]
