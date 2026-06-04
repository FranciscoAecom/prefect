from core.treatment.context import replace_treatment_context as replace_context
from core.spatial.repair import repair_invalid_geometries
from core.output.identifiers import assign_output_identifiers
from core.treatment.steps.postprocess_functions import apply_postprocess_functions
from core.spatial.metrics import fill_missing_spatial_metrics
from core.utils import timed_log_step


def postprocess_step(context):
    final_gdf = context.final_gdf
    with timed_log_step("Atribuicao de identificadores finais"):
        final_gdf = assign_output_identifiers(final_gdf, context.id_start)
    with timed_log_step("Reparo de geometrias invalidas"):
        final_gdf = repair_invalid_geometries(final_gdf)
    final_gdf = apply_postprocess_functions(
        final_gdf,
        context.rule_profile or {},
        record=context.record,
        project_name=context.project_name,
        rule_profile_name=context.rule_profile_name,
    )
    with timed_log_step("Complemento de metricas espaciais"):
        final_gdf = fill_missing_spatial_metrics(final_gdf)
    return replace_context(context, final_gdf=final_gdf)
