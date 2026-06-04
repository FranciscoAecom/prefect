from prefect import flow

from core.tasks.raster import optimize_raster_task


@flow(name="Raster Pipeline", log_prints=True)
def raster_pipeline_flow(
    input_raster,
    output_raster=None,
    source_epsg=None,
    dst_epsg=4326,
    nodata_mode="auto",
    custom_nodata=None,
    resampling_mode="auto",
):
    return optimize_raster_task(
        input_raster=input_raster,
        output_raster=output_raster,
        source_epsg=source_epsg,
        dst_epsg=dst_epsg,
        nodata_mode=nodata_mode,
        custom_nodata=custom_nodata,
        resampling_mode=resampling_mode,
    )


__all__ = ["raster_pipeline_flow"]
