from prefect import flow

from core.publish.config import PublishOptions
from core.publish.execution import publish_folder_items
from core.publish.queue import load_publish_queue
from core.tasks.publish import discover_publish_items_task, publish_item_task
from core.utils import log


@flow(name="Data Publish", log_prints=True)
def data_publish_flow(
    folder=None,
    theme_folders=None,
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
    folders = [folder] if folder else load_publish_folders_from_ingest(theme_folders)
    for publish_folder in folders:
        items = discover_publish_items_task(
            publish_folder,
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


def load_publish_folders_from_ingest(theme_folders=None):
    records, issues, summary = load_publish_queue(theme_folders=theme_folders)
    log("Resumo da planilha ingest para publicacao:")
    log(f"  Registros lidos: {summary['total_records']}")
    log("  Flag elegivel: publish")
    log(f"  Registros com flag publish: {summary['publish_candidates']}")
    log(f"  Pastas aptas para publicacao: {summary['eligible_records']}")
    log(f"  Registros ignorados com excecao: {summary['issues']}")
    for issue in issues:
        log(
            "  Issue publicacao | "
            f"linha={issue.sheet_row} | theme_folder={issue.theme_folder} | "
            f"motivo={issue.reason}"
        )
    return [record.silver_dir for record in records]


def publish_record_outputs(
    record,
    fallback_output_dir,
    **publish_kwargs,
):
    output_dir = getattr(record, "output_dir", "") or fallback_output_dir
    log(f"Iniciando publicacao automatica da pasta silver: {output_dir}")
    items = discover_publish_items_task(output_dir)
    for item in items:
        publish_item_task(item, **publish_kwargs)


def publish_record_outputs_direct(
    output_dir,
    config,
    credentials,
    dry_run=False,
    skip_geoserver=False,
    skip_data=False,
    skip_catalog=False,
):
    log(f"Iniciando publicacao automatica da pasta silver: {output_dir}")
    publish_folder_items(
        output_dir,
        config,
        credentials,
        dry_run=dry_run,
        skip_geoserver=skip_geoserver,
        skip_data=skip_data,
        skip_catalog=skip_catalog,
    )


__all__ = [
    "data_publish_flow",
    "load_publish_folders_from_ingest",
    "publish_record_outputs",
    "publish_record_outputs_direct",
]
