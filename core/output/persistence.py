from core.io.dataset import write_output_gpkg
from core.metadata import persist_stage_metadata_xmls
from core.output.columns import drop_internal_output_columns
from core.output.paths import resolve_output_path
from core.output.quality import build_output_quality_summary, log_output_quality_summary
from core.output.secondary_outputs import persist_secondary_outputs
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
    log("Fluxo 6/7 - Salvando dado tratado no silver")
    persisted_output_path = persist_output_dataset(export_gdf, output_path, persist_dataset)
    secondary_output_paths = persist_configured_secondary_outputs(
        export_gdf,
        theme_output_dir,
        base_name,
        persist_dataset,
        rule_profile or {},
    )
    if persisted_output_path:
        log("Fluxo 7/7 - Criando XML do silver")
        persist_stage_metadata_xmls(
            record,
            export_gdf,
            [persisted_output_path, *(secondary_output_paths or [])],
            base_name,
            persist_dataset=persist_dataset,
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
