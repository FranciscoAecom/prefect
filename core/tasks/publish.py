from prefect import task

from core.publish.config import PublishOptions
from core.publish.execution import discover_items_for_publish, publish_item_to_targets
from core.utils import log


@task(name="Descobrir arquivos para publicacao", log_prints=True)
def discover_publish_items_task(folder, store=None, layer=None, style=None, layer_title=None):
    items = discover_items_for_publish(
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
    options = PublishOptions(
        environment=environment,
        workspace=workspace,
        geoserver=geoserver,
        catalog=catalog,
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

    publish_item_to_targets(
        item,
        options.build_config(),
        options.load_credentials(),
        **options.execution_kwargs(),
    )


__all__ = ["discover_publish_items_task", "publish_item_task"]
