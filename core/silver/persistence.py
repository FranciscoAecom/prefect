from core.io.dataset import write_output_gpkg
from core.output.columns import drop_internal_output_columns
from core.output.paths import resolve_output_path
from core.output.quality import build_output_quality_summary, log_output_quality_summary
from core.output.secondary_outputs import persist_secondary_outputs
from core.processing.stages import FLOW_STAGE_SAVE_SILVER
from core.silver.artifacts import persist_silver_artifacts
from core.silver.primary_output import prepare_primary_output_gdf
from core.utils import log


def save_outputs(
    final_gdf,
    record,
    output_dir,
    use_configured_final_name=False,
    persist_dataset=True,
    rule_profile=None,
):
    theme_output_dir, base_name, output_path = resolve_output_path(
        record,
        output_dir,
        use_configured_final_name,
    )
    export_gdf = drop_internal_output_columns(final_gdf)
    primary_export_gdf = prepare_primary_output_gdf(export_gdf, rule_profile or {})
    log(FLOW_STAGE_SAVE_SILVER)
    persisted_output_path = persist_output_dataset(primary_export_gdf, output_path, persist_dataset)
    secondary_outputs = persist_configured_secondary_outputs(
        export_gdf,
        theme_output_dir,
        base_name,
        persist_dataset,
        rule_profile or {},
    )
    if persisted_output_path:
        persisted_outputs = [
            {"path": persisted_output_path, "gdf": primary_export_gdf},
            *(secondary_outputs or []),
        ]
        persist_silver_artifacts(
            record,
            export_gdf,
            persisted_outputs,
            base_name,
            persist_dataset=persist_dataset,
            rule_profile=rule_profile or {},
        )
    quality_summary = build_output_quality_summary(final_gdf, theme_output_dir, base_name)
    log_output_quality_summary(quality_summary)

    return persisted_output_path


def persist_output_dataset(export_gdf, output_path, persist_dataset):
    if persist_dataset:
        log(f"Salvando resultado em {output_path}")
        write_output_gpkg(
            export_gdf,
            output_path,
            overwrite_existing=True,
        )
        log("Arquivo salvo com sucesso")
        return output_path

    log(
        "Saida individual omitida porque a consolidacao em grupo esta habilitada "
        "e KEEP_INDIVIDUAL_OUTPUTS_WHEN_GROUPING=False."
    )
    return None


def persist_configured_secondary_outputs(
    export_gdf,
    theme_output_dir,
    base_name,
    persist_dataset,
    rule_profile,
):
    return persist_secondary_outputs(
        export_gdf,
        rule_profile,
        theme_output_dir,
        base_name,
        persist_dataset,
    )


__all__ = [
    "prepare_primary_output_gdf",
    "persist_configured_secondary_outputs",
    "persist_output_dataset",
    "save_outputs",
]
