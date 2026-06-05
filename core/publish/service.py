from core.publish.execution import publish_folder_items
from core.publish.records import load_publish_records
from core.tasks.publish import discover_publish_items_task, publish_item_task
from core.utils import log


def run_data_publish(
    folders,
    options,
    store=None,
    layer=None,
    style=None,
    layer_title=None,
):
    for publish_folder in folders:
        items = discover_publish_items_task(
            publish_folder,
            store=store,
            layer=layer,
            style=style,
            layer_title=layer_title,
        )
        for item in items:
            publish_item_task(item, **options.task_kwargs())


def load_publish_folders_from_ingest(theme_folders=None):
    records, issues, summary = load_publish_records(theme_folders=theme_folders)
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
    "load_publish_folders_from_ingest",
    "publish_record_outputs",
    "publish_record_outputs_direct",
    "run_data_publish",
]
