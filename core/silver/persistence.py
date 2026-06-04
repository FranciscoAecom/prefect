from core.io.dataset import write_output_gpkg
from core.output.columns import drop_internal_output_columns
from core.output.paths import resolve_output_path
from core.output.quality import build_output_quality_summary, log_output_quality_summary
from core.treatment.steps.stages import FLOW_STAGE_SAVE_SILVER
from core.silver.artifacts import persist_silver_artifacts
from core.silver.manifest import (
    SilverDatasetOutput,
    SilverOutputManifest,
    persist_silver_manifest,
    quality_reports_from_summary,
)
from core.silver.output_adjustments import prepare_output_adjustments_gdf
from core.utils import log


def save_outputs(
    final_gdf,
    record,
    output_dir,
    use_configured_final_name=False,
    persist_dataset=True,
    rule_profile=None,
):
    manifest = save_outputs_manifest(
        final_gdf,
        record,
        output_dir,
        use_configured_final_name=use_configured_final_name,
        persist_dataset=persist_dataset,
        rule_profile=rule_profile,
    )
    return manifest.primary_output_path


def save_outputs_manifest(
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
    primary_export_gdf = prepare_output_adjustments_gdf(export_gdf, rule_profile or {})
    log(FLOW_STAGE_SAVE_SILVER)
    persisted_output_path = persist_output_dataset(primary_export_gdf, output_path, persist_dataset)
    manifest = build_initial_silver_manifest(persisted_output_path)
    if persisted_output_path:
        persisted_outputs = [
            {
                "path": persisted_output_path,
                "gdf": primary_export_gdf,
                "role": "primary",
                "label": "principal",
            },
        ]
        xml_paths, sld_paths = persist_silver_artifacts(
            record,
            export_gdf,
            persisted_outputs,
            base_name,
            persist_dataset=persist_dataset,
            rule_profile=rule_profile or {},
        )
        manifest = manifest.with_artifacts(xml_paths, sld_paths)
    quality_summary = build_output_quality_summary(
        final_gdf,
        theme_output_dir,
        base_name,
        rule_profile=rule_profile or {},
    )
    log_output_quality_summary(quality_summary)
    manifest = manifest.with_quality_reports(
        quality_reports_from_summary(quality_summary)
    )
    manifest = persist_silver_manifest(
        manifest,
        theme_output_dir,
        base_name,
        persist_dataset=persist_dataset,
    )

    return manifest


def build_initial_silver_manifest(primary_output_path):
    primary_output = None
    if primary_output_path:
        primary_output = SilverDatasetOutput(
            path=primary_output_path,
            role="primary",
            label="principal",
        )
    return SilverOutputManifest(primary_output=primary_output)


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


__all__ = [
    "build_initial_silver_manifest",
    "prepare_output_adjustments_gdf",
    "persist_output_dataset",
    "save_outputs",
    "save_outputs_manifest",
]
