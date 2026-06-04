from core.treatment.steps.bronze_step import persist_bronze_step
from core.treatment.steps.errors import log_treatment_error
from core.treatment.steps.input_step import load_input_step
from core.treatment.steps.mapping_step import prepare_mapping_step
from core.treatment.steps.output_step import persist_outputs_step
from core.treatment.steps.pipeline_step import run_configured_treatment_step
from core.treatment.steps.postprocess_step import postprocess_step
from core.treatment.steps.rules_step import attach_rule_profile_step
from core.treatment.steps.schema_step import validate_input_schema_step
from core.treatment.steps.stages import (
    FLOW_STAGE_BRONZE_AND_XML,
    FLOW_STAGE_READ_TEMP,
    FLOW_STAGE_SILVER_AND_XML,
    FLOW_STAGE_TREATMENTS,
)
from core.treatment.steps.summary import log_dataset_overview
from core.utils import timed_log_step


def run_treatment_steps(
    context,
    autofix_service,
    use_configured_final_name=False,
    persist_individual_output=True,
):
    context = _run_timed_step(
        FLOW_STAGE_READ_TEMP,
        "Erro ao carregar ou validar arquivo de entrada",
        lambda: load_input_step(context),
    )
    if context is None:
        return None

    context = _run_timed_step(
        FLOW_STAGE_BRONZE_AND_XML,
        "Erro ao materializar bronze ou XML do bronze",
        lambda: persist_bronze_step(
            context,
            use_configured_final_name=use_configured_final_name,
        ),
    )
    if context is None:
        return None

    context = _run_timed_step(
        "Carregamento do perfil de regras",
        "Erro ao carregar perfil de regras",
        lambda: attach_rule_profile_step(context),
    )
    if context is None:
        return None

    context = _run_timed_step(
        "Validacao de schema tabular",
        "Erro na validacao de schema tabular",
        lambda: validate_input_schema_step(context),
    )
    if context is None:
        return None

    log_dataset_overview(context.gdf)

    with timed_log_step("Preparacao do mapeamento de validacao"):
        context = prepare_mapping_step(context)

    with timed_log_step(FLOW_STAGE_TREATMENTS):
        context = run_configured_treatment_step(context)

    context = postprocess_step(context)
    autofix_summary = autofix_service.autofix_rule_profile(context, context.final_gdf)
    autofix_service.log_autofix_summary(autofix_summary)

    return _run_timed_step(
        FLOW_STAGE_SILVER_AND_XML,
        "Erro ao salvar arquivo",
        lambda: persist_outputs_step(
            context,
            use_configured_final_name=use_configured_final_name,
            persist_dataset=persist_individual_output,
        ),
    )


def _run_timed_step(label, error_message, operation):
    try:
        with timed_log_step(label):
            return operation()
    except Exception as exc:
        log_treatment_error(error_message, exc)
        return None


__all__ = ["run_treatment_steps"]
