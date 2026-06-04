from pathlib import Path

from core.processing.result import ProcessRecordResult
from core.raster.processing import build_raster_request, process_raster_request


def process_raster_record(record, output_dir):
    record_output_dir = Path(getattr(record, "output_dir", "") or output_dir)
    record_output_dir.mkdir(parents=True, exist_ok=True)
    input_path = Path(record.input_path)
    output_path = record_output_dir / f"{input_path.stem}_wgs84_lzw.tif"

    request = build_raster_request(
        input_raster=input_path,
        output_raster=output_path,
        source_epsg=getattr(record, "raster_source_epsg", None),
        nodata_mode=getattr(record, "raster_nodata_mode", "auto") or "auto",
        custom_nodata=getattr(record, "raster_custom_nodata", None),
        resampling_mode=getattr(record, "raster_resampling_mode", "auto") or "auto",
    )
    result = process_raster_request(request)
    return ProcessRecordResult(
        processed_count=1,
        output_path=result.output_raster,
        final_gdf=None,
    )


__all__ = ["process_raster_record"]
