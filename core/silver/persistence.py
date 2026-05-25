from core.io.dataset import write_output_gpkg
from core.metadata import persist_stage_metadata_xmls
from core.output.columns import drop_internal_output_columns
from core.output.paths import resolve_output_path
from core.output.quality import build_output_quality_summary, log_output_quality_summary
from core.output.secondary_outputs import persist_secondary_outputs
from core.processing.stages import FLOW_STAGE_CREATE_SILVER_XML, FLOW_STAGE_SAVE_SILVER
from core.spatial.brazil_bounds import relocate_geometries_outside_brazil_bounds_to_centroid
from core.sld import persist_stage_slds
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
        log(FLOW_STAGE_CREATE_SILVER_XML)
        persist_stage_metadata_xmls(
            record,
            export_gdf,
            [output["path"] for output in persisted_outputs],
            base_name,
            persist_dataset=persist_dataset,
        )
        persist_stage_slds(
            persisted_outputs,
            rule_profile=rule_profile or {},
            persist_dataset=persist_dataset,
        )
    quality_summary = build_output_quality_summary(final_gdf, theme_output_dir, base_name)
    log_output_quality_summary(quality_summary)

    return persisted_output_path


def prepare_primary_output_gdf(export_gdf, rule_profile):
    primary_output = rule_profile.get("primary_output", {}) or {}
    if not primary_output.get("relocate_outside_brazil_bounds_to_centroid"):
        return export_gdf

    relocated = relocate_geometries_outside_brazil_bounds_to_centroid(export_gdf)
    moved_count = count_changed_geometries(export_gdf, relocated)
    if moved_count:
        log(
            "Saida completa: "
            f"{moved_count} geometria(s) fora do limite Brasil / zona costeira "
            "foram reposicionadas para o centroide unico do limite brasileiro."
        )
    return relocated


def count_changed_geometries(before_gdf, after_gdf):
    if "geometry" not in before_gdf.columns or "geometry" not in after_gdf.columns:
        return 0
    changed = before_gdf.geometry.geom_equals(after_gdf.geometry)
    return int((~changed.fillna(False)).sum())


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
