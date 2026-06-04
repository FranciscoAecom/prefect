from contextlib import ExitStack

from core.execution_locks import named_execution_lock
from core.ingest.run_request import IngestRunRequest
from core.processing.service import ProcessingService
from core.queue.group_state import QueueGroupState
from core.queue.settings import QueueRunSettings
from core.utils import log


TreatmentService = ProcessingService


def run_data_treatment(output_base=None, theme_folders=None, source_path_overrides=None, force=False):
    from core.tasks.treatment import prepare_treatment_queue_task, run_treatment_record_task

    settings = QueueRunSettings.from_output_base(output_base)
    run_request = IngestRunRequest.from_legacy(
        theme_folders=theme_folders,
        source_path_overrides=source_path_overrides,
        force=force,
    )
    queue_filter = run_request.queue_filter

    with _queue_filter_locks(queue_filter):
        queue_context = prepare_treatment_queue_task(
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
            run_treatment_record_task(
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


__all__ = ["TreatmentService", "run_data_treatment"]
