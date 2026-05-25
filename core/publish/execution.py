from core.publish.geonetwork import import_metadata_to_geonetwork
from core.publish.geoserver import publish_to_geoserver
from core.publish.metadata import MultiplePublishItemsError, discover_publish_items
from core.utils import log


def log_publish_context(item, config):
    log(f"Publicando layer: {item.layer}")
    log(f"Ambiente: {getattr(config, 'environment', '')}")
    log(f"GeoServer: {getattr(config, 'geoserver', '')}")
    log(f"GeoNetwork: {getattr(config, 'catalog', '')}")
    log(f"Workspace: {getattr(config, 'workspace', '')}")


def publish_item_to_targets(
    item,
    config,
    credentials,
    dry_run=False,
    skip_geoserver=False,
    skip_data=False,
    skip_catalog=False,
):
    log_publish_context(item, config)
    if skip_geoserver:
        log("Etapas do GeoServer ignoradas por parametro.")
        attribute_types = {}
    else:
        attribute_types = publish_to_geoserver(
            item,
            config,
            credentials,
            dry_run=dry_run,
            skip_data=skip_data,
        )

    if skip_catalog:
        log("Importacao GeoNetwork ignorada por parametro.")
    else:
        import_metadata_to_geonetwork(
            item,
            config,
            credentials,
            dry_run=dry_run,
            attribute_types=attribute_types,
        )

    log(f"Publicacao concluida: {item.layer}")


def discover_items_for_publish(folder, **kwargs):
    try:
        return discover_publish_items(folder, **kwargs)
    except MultiplePublishItemsError as exc:
        log(str(exc))
        return []


def publish_folder_items(
    folder,
    config,
    credentials,
    dry_run=False,
    skip_geoserver=False,
    skip_data=False,
    skip_catalog=False,
):
    items = discover_items_for_publish(folder)
    for item in items:
        publish_item_to_targets(
            item,
            config,
            credentials,
            dry_run=dry_run,
            skip_geoserver=skip_geoserver,
            skip_data=skip_data,
            skip_catalog=skip_catalog,
        )


__all__ = [
    "discover_items_for_publish",
    "log_publish_context",
    "publish_folder_items",
    "publish_item_to_targets",
]
