from prefect import task
from prefect.events import emit_event

from core.ingest.run_request import IngestRunRequest
from core.prefect_support.run_names import record_task_run_name
from core.treatment.run_loader import prepare_treatment_run
from core.treatment.runner import run_treatment_record


@task(name="Preparar tratamento", log_prints=True)
def prepare_treatment_run_task(
    output_base,
    theme_folders=None,
    source_path_overrides=None,
    force=False,
    scheduled=False,
):
    run_request = IngestRunRequest.from_parameters(
        theme_folders=theme_folders,
        source_path_overrides=source_path_overrides,
        force=force,
        scheduled=scheduled,
    )
    return prepare_treatment_run(
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


@task(name="Emitir evento tratamento concluido", log_prints=True)
def emit_treatment_completed_event_task(theme_folders):
    normalized_theme_folders = sorted({str(theme_folder) for theme_folder in theme_folders})
    if not normalized_theme_folders:
        return None

    event = emit_event(
        event="dataset.treatment.completed",
        resource={
            "prefect.resource.id": "dataset.treatment.completed",
            "prefect.resource.name": "Tratamento concluido",
        },
        payload={"theme_folders": normalized_theme_folders},
    )
    return str(event.id) if event else None


__all__ = [
    "emit_treatment_completed_event_task",
    "prepare_treatment_run_task",
    "run_treatment_record_task",
]
