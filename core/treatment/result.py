from dataclasses import dataclass

import geopandas as gpd


@dataclass(frozen=True)
class TreatmentRecordResult:
    processed_count: int
    output_path: str | None
    final_gdf: gpd.GeoDataFrame | None


def treatment_failure_result():
    return TreatmentRecordResult(0, None, None)


def treatment_success_result(context):
    return TreatmentRecordResult(
        len(context.final_gdf),
        context.output_path,
        context.final_gdf,
    )


__all__ = [
    "TreatmentRecordResult",
    "treatment_failure_result",
    "treatment_success_result",
]
