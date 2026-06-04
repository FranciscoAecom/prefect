from prefect import flow

from core.publish.config import PublishOptions
from core.tasks.publish import discover_publish_items_task, publish_item_task


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
            **options.task_kwargs(),
        )


__all__ = ["data_publish_flow"]
