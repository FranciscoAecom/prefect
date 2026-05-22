from core.processing.errors import log_processing_error
from core.processing.bronze_step import persist_bronze_step
from core.processing.input_step import load_input_step
from core.processing.mapping_step import prepare_mapping_step
from core.processing.output_step import persist_outputs_step
from core.processing.pipeline_step import run_pipeline_step
from core.processing.postprocess_step import postprocess_step
from core.processing.rules_step import attach_rule_profile_step
from core.processing.schema_step import validate_input_schema_step
from core.processing.summary import log_dataset_overview
from core.utils import timed_log_step


def run_processing_pipeline(
    context,
    autofix_service,
    use_configured_final_name=False,
    persist_individual_output=True,
):
    context = _run_timed_step(
        "Fluxo 1/7 - Ler arquivo no temp",
        "Erro ao carregar ou validar arquivo de entrada",
        lambda: load_input_step(context),
    )
    if context is None:
        return None

    context = _run_timed_step(
        "Fluxo 2/7 a 4/7 - Bronze e XML do bronze",
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

    with timed_log_step("Fluxo 5/7 - Fazer tratamentos"):
        context = run_pipeline_step(context)

    context = postprocess_step(context)
    autofix_summary = autofix_service.autofix_rule_profile(context, context.final_gdf)
    autofix_service.log_autofix_summary(autofix_summary)

    return _run_timed_step(
        "Fluxo 6/7 e 7/7 - Salvar silver e XML do silver",
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
        log_processing_error(error_message, exc)
        return None
