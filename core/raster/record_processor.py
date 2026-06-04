from pathlib import Path

from core.bronze import ensure_bronze_dataset
from core.output.paths import resolve_output_path
from core.processing.result import ProcessRecordResult
from core.processing.stages import (
    FLOW_STAGE_BRONZE_AND_XML,
    FLOW_STAGE_SAVE_SILVER,
    FLOW_STAGE_SILVER_AND_XML,
    FLOW_STAGE_TREATMENTS,
)
from core.raster.processing import build_raster_request, process_raster_request
from core.utils import log, timed_log_step


def process_raster_record(record, output_dir, use_configured_final_name=False):
    input_path = Path(record.input_path)
    output_path = resolve_raster_output_path(
        record,
        output_dir,
        use_configured_final_name=use_configured_final_name,
    )

    with timed_log_step(FLOW_STAGE_BRONZE_AND_XML):
        bronze_dataset_path = ensure_bronze_dataset(record)
        if bronze_dataset_path:
            log(
                f"{FLOW_STAGE_BRONZE_AND_XML}: arquivo bruto preservado no bronze: "
                f"{bronze_dataset_path}"
            )
        else:
            log(
                f"{FLOW_STAGE_BRONZE_AND_XML}: bronze nao gerado porque nao foi "
                "encontrado dado bruto elegivel"
            )

    request = build_raster_request(
        input_raster=input_path,
        output_raster=output_path,
        source_epsg=getattr(record, "raster_source_epsg", None),
        nodata_mode=getattr(record, "raster_nodata_mode", "auto") or "auto",
        custom_nodata=getattr(record, "raster_custom_nodata", None),
        resampling_mode=getattr(record, "raster_resampling_mode", "auto") or "auto",
    )

    with timed_log_step(FLOW_STAGE_TREATMENTS):
        log(FLOW_STAGE_SAVE_SILVER)
        log(f"Salvando raster tratado em {output_path}")
        result = process_raster_request(request)

    log(f"{FLOW_STAGE_SILVER_AND_XML}: raster tratado salvo no silver: {result.output_raster}")
    return ProcessRecordResult(
        processed_count=1,
        output_path=result.output_raster,
        final_gdf=None,
    )


def resolve_raster_output_path(record, output_dir, use_configured_final_name=False):
    _, _, output_path = resolve_output_path(
        record,
        output_dir,
        use_configured_final_name,
    )
    output_path = Path(output_path).with_suffix(".tif")
    output_path.parent.mkdir(parents=True, exist_ok=True)
    return output_path


__all__ = ["process_raster_record", "resolve_raster_output_path"]
