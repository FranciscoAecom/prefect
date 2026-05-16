from contextlib import ExitStack

from prefect import flow, task

from core.execution_locks import named_execution_lock
from core.prefect_support.run_names import flow_run_name, record_task_run_name
from core.queue.filters import QueueFilter
from core.queue.group_state import QueueGroupState
from core.queue.queue_loader import prepare_processing_queue
from core.queue.record_runner import run_queue_record
from core.queue.settings import QueueRunSettings
from core.utils import log


@task(name="Preparar fila de processamento", log_prints=True)
def prepare_queue_task(output_base, theme_folders=None):
    return prepare_processing_queue(
        output_base,
        queue_filter=QueueFilter.from_theme_folders(theme_folders),
    )


@task(
    name="Processar registro da fila",
    task_run_name=record_task_run_name,
    log_prints=True,
)
def run_queue_record_task(
    record,
    output_dir,
    group_state,
    keep_individual_outputs_when_grouping,
):
    run_queue_record(
        record,
        output_dir,
        group_state,
        keep_individual_outputs_when_grouping=keep_individual_outputs_when_grouping,
    )


@flow(name="Data Pipeline", flow_run_name=flow_run_name, log_prints=True)
def data_pipeline_flow(output_base=None, theme_folders=None):
    settings = QueueRunSettings.from_output_base(output_base)
    queue_filter = QueueFilter.from_theme_folders(theme_folders)

    with _queue_filter_locks(queue_filter):
        queue_context = prepare_queue_task(settings.output_base, theme_folders)
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

        log("Processamento finalizado")


def _queue_filter_locks(queue_filter):
    stack = ExitStack()
    for theme_folder in sorted(queue_filter.theme_folders):
        stack.enter_context(named_execution_lock(f"queue-{theme_folder}"))
    return stack
