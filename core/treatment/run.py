from core.ingest.run_request import IngestRunRequest
from core.ingest.filters import ThemeFolderFilter
from core.treatment.group_state import TreatmentGroupState
from core.treatment.run_loader import prepare_treatment_run
from core.treatment.record_runner import run_treatment_record
from core.treatment.settings import TreatmentRunSettings
from core.utils import log


def run_treatment(
    output_base=None,
    settings=None,
    theme_folders=None,
    theme_filter=None,
    run_request=None,
    force=False,
    scheduled=False,
):
    settings = settings or TreatmentRunSettings.from_output_base(output_base)
    run_request = run_request or IngestRunRequest.from_parameters(
        theme_folders=theme_folders,
        theme_filter=theme_filter,
        force=force,
        scheduled=scheduled,
    )
    treatment_context = prepare_treatment_run(
        settings.output_base,
        run_request=run_request,
    )
    if treatment_context is None:
        return

    group_state = TreatmentGroupState(
        treatment_context.records,
        enable_group_consolidation=settings.enable_group_consolidation,
    )

    for record in treatment_context.records:
        run_treatment_record(
            record,
            treatment_context.output_dir,
            group_state,
            keep_individual_outputs_when_grouping=(
                settings.keep_individual_outputs_when_grouping
            ),
        )

    log("Tratamento finalizado")


__all__ = ["run_treatment"]
