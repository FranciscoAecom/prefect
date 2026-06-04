from prefect import task

from core.raster.processing import build_raster_request, process_raster_request


@task(name="Otimizar raster GDAL", log_prints=True)
def optimize_raster_task(
    input_raster,
    output_raster=None,
    source_epsg=None,
    dst_epsg=4326,
    nodata_mode="auto",
    custom_nodata=None,
    resampling_mode="auto",
):
    request = build_raster_request(
        input_raster=input_raster,
        output_raster=output_raster,
        source_epsg=source_epsg,
        dst_epsg=dst_epsg,
        nodata_mode=nodata_mode,
        custom_nodata=custom_nodata,
        resampling_mode=resampling_mode,
    )
    return process_raster_request(request)


__all__ = ["optimize_raster_task"]
