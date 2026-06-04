from contextlib import ExitStack

from prefect import flow

from core.execution_locks import named_execution_lock
from core.ingest.run_request import IngestRunRequest
from core.prefect_support.run_names import flow_run_name
from core.publish.config import PublishOptions
from core.publish.execution import publish_folder_items
from core.queue.group_state import QueueGroupState
from core.queue.queue_loader import prepare_processing_queue
from core.queue.record_runner import run_queue_record
from core.queue.settings import QueueRunSettings
from core.tasks.pipeline import prepare_queue_task, run_queue_record_task
from core.tasks.publish import discover_publish_items_task, publish_item_task
from core.utils import log


@flow(name="Data Pipeline Publish", flow_run_name=flow_run_name, log_prints=True)
def data_pipeline_publish_flow(
    output_base=None,
    theme_folders=None,
    source_path_overrides=None,
    environment="qas",
    workspace="gold",
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
    dry_run_publish=False,
    skip_geoserver=False,
    skip_data=False,
    skip_catalog=False,
    force=False,
):
    publish_options = PublishOptions(
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
        dry_run=dry_run_publish,
        skip_geoserver=skip_geoserver,
        skip_data=skip_data,
        skip_catalog=skip_catalog,
    )
    settings = QueueRunSettings.from_output_base(output_base)
    run_request = IngestRunRequest.from_legacy(
        theme_folders=theme_folders,
        source_path_overrides=source_path_overrides,
        force=force,
    )
    queue_filter = run_request.queue_filter

    with _queue_filter_locks(queue_filter):
        queue_context = prepare_queue_task(
            settings.output_base,
            theme_folders,
            source_path_overrides,
            force,
        )
        if queue_context is None:
            return

        group_state = QueueGroupState(
            queue_context.records,
            enable_group_consolidation=settings.enable_group_consolidation,
        )

        for record in queue_context.records:
            run_queue_record_task(
                record,
                queue_context.output_dir,
                group_state,
                settings.keep_individual_outputs_when_grouping,
            )
            publish_record_outputs(
                record,
                queue_context.output_dir,
                **publish_options.task_kwargs(),
            )

        log("Processamento e publicacao finalizados")


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


def run_pipeline_publish_direct(
    output_base=None,
    theme_folders=None,
    source_path_overrides=None,
    environment="qas",
    workspace="gold",
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
    dry_run_publish=False,
    skip_geoserver=False,
    skip_data=False,
    skip_catalog=False,
    force=False,
):
    publish_options = PublishOptions(
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
        dry_run=dry_run_publish,
        skip_geoserver=skip_geoserver,
        skip_data=skip_data,
        skip_catalog=skip_catalog,
    )
    settings = QueueRunSettings.from_output_base(output_base)
    run_request = IngestRunRequest.from_legacy(
        theme_folders=theme_folders,
        source_path_overrides=source_path_overrides,
        force=force,
    )
    queue_filter = run_request.queue_filter
    config = publish_options.build_config()
    credentials = publish_options.load_credentials()

    with _queue_filter_locks(queue_filter):
        queue_context = prepare_processing_queue(
            settings.output_base,
            run_request=run_request,
        )
        if queue_context is None:
            return

        group_state = QueueGroupState(
            queue_context.records,
            enable_group_consolidation=settings.enable_group_consolidation,
        )

        for record in queue_context.records:
            run_queue_record(
                record,
                queue_context.output_dir,
                group_state,
                keep_individual_outputs_when_grouping=(
                    settings.keep_individual_outputs_when_grouping
                ),
            )
            publish_record_outputs_direct(
                getattr(record, "output_dir", "") or queue_context.output_dir,
                config,
                credentials,
                **publish_options.execution_kwargs(),
            )

    log("Processamento e publicacao finalizados")


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


def _queue_filter_locks(queue_filter):
    stack = ExitStack()
    for theme_folder in sorted(queue_filter.theme_folders):
        stack.enter_context(named_execution_lock(f"queue-{theme_folder}"))
    return stack


__all__ = [
    "data_pipeline_publish_flow",
    "publish_record_outputs",
    "publish_record_outputs_direct",
    "run_pipeline_publish_direct",
]
