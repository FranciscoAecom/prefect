from core.spatial.brazil_bounds import relocate_geometries_outside_brazil_bounds_to_centroid
from core.utils import log


RELOCATE_OUTSIDE_BRAZIL_BOUNDS_KEY = "relocate_outside_brazil_bounds_to_centroid"


def prepare_primary_output_gdf(export_gdf, rule_profile):
    primary_output = rule_profile.get("primary_output", {}) or {}
    if not primary_output.get(RELOCATE_OUTSIDE_BRAZIL_BOUNDS_KEY):
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


__all__ = [
    "RELOCATE_OUTSIDE_BRAZIL_BOUNDS_KEY",
    "count_changed_geometries",
    "prepare_primary_output_gdf",
]
