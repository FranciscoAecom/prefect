from core.ingest.run_request import IngestRunRequest
from core.ingest.filters import QueueFilter
from core.treatment.group_state import QueueGroupState
from core.treatment.queue_loader import prepare_treatment_queue
from core.treatment.record_runner import run_treatment_record
from core.treatment.settings import QueueRunSettings
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
        run_treatment_record(
            record,
            queue_context.output_dir,
            group_state,
            keep_individual_outputs_when_grouping=(
                settings.keep_individual_outputs_when_grouping
            ),
        )

    log("Processamento finalizado")


__all__ = ["run_treatment_queue"]
