from prefect import task

from core.ingest.run_request import IngestRunRequest
from core.prefect_support.run_names import record_task_run_name
from core.treatment.run_loader import prepare_treatment_queue
from core.treatment.runner import run_treatment_record


@task(name="Preparar tratamento", log_prints=True)
def prepare_treatment_queue_task(output_base, theme_folders=None, source_path_overrides=None, force=False):
    run_request = IngestRunRequest.from_legacy(
        theme_folders=theme_folders,
        source_path_overrides=source_path_overrides,
        force=force,
    )
    return prepare_treatment_queue(
        output_base,
        run_request=run_request,
    )


@task(
    name="Tratar registro",
    task_run_name=record_task_run_name,
    log_prints=True,
)
def run_treatment_record_task(
    record,
    output_dir,
    group_state,
    keep_individual_outputs_when_grouping,
):
    run_treatment_record(
        record,
        output_dir,
        group_state,
        keep_individual_outputs_when_grouping=keep_individual_outputs_when_grouping,
    )


__all__ = [
    "prepare_treatment_queue_task",
    "run_treatment_record_task",
]
