import warnings

from core.queue.group_state import QueueGroupState
from core.ingest.run_request import IngestRunRequest
from core.queue.filters import QueueFilter
from core.queue.queue_loader import prepare_treatment_queue
from core.queue.record_runner import run_queue_record
from core.queue.settings import QueueRunSettings
from core.utils import log


def run_treatment_queue(
    output_base=None,
    settings=None,
    theme_folders=None,
    queue_filter=None,
    run_request=None,
    force=False,
):
    settings = settings or QueueRunSettings.from_output_base(output_base)
    run_request = run_request or IngestRunRequest.from_legacy(
        theme_folders=theme_folders,
        queue_filter=queue_filter,
        force=force,
    )
    queue_context = prepare_treatment_queue(
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

    log("Processamento finalizado")


def run_processing_queue(*args, **kwargs):
    warnings.warn(
        "run_processing_queue() esta depreciado; use run_treatment_queue().",
        DeprecationWarning,
        stacklevel=2,
    )
    return run_treatment_queue(*args, **kwargs)
