from pathlib import Path

from core.raster.gdal_backend import (
    analyze_raster_values,
    build_internal_overviews,
    configure_gdal,
    get_epsg_from_dataset,
    open_raster_readonly,
    resolve_source_wkt,
    run_translate_or_warp,
)
from core.raster.models import (
    RasterOptimizationOptions,
    RasterOptimizationRequest,
    RasterOptimizationResult,
)
from core.raster.optimization import (
    choose_best_dtype,
    choose_resampling,
    resolve_nodata,
)
from core.utils import log


def build_raster_request(
    input_raster,
    output_raster=None,
    source_epsg=None,
    dst_epsg=4326,
    nodata_mode="auto",
    custom_nodata=None,
    resampling_mode="auto",
):
    input_path = Path(input_raster).resolve()
    output_path = (
        Path(output_raster).resolve()
        if output_raster
        else input_path.with_name(f"{input_path.stem}_wgs84_lzw.tif")
    )
    if output_path.suffix.lower() not in [".tif", ".tiff"]:
        output_path = output_path.with_suffix(".tif")

    return RasterOptimizationRequest(
        input_raster=input_path,
        output_raster=output_path,
        source_epsg=source_epsg,
        options=RasterOptimizationOptions(
            dst_epsg=dst_epsg,
            nodata_mode=nodata_mode,
            custom_nodata=custom_nodata,
            resampling_mode=resampling_mode,
        ),
    )


def process_raster_request(request):
    options = request.options
    configure_gdal(options)

    input_raster = Path(request.input_raster)
    output_raster = Path(request.output_raster)
    if not input_raster.exists() or not input_raster.is_file():
        raise FileNotFoundError(f"Raster de entrada nao encontrado: {input_raster}")

    log("Iniciando otimizacao raster")
    log(f"  Entrada: {input_raster}")
    log(f"  Saida: {output_raster}")

    dataset = open_raster_readonly(input_raster)
    try:
        detected_epsg = get_epsg_from_dataset(dataset)
        src_epsg = detected_epsg or request.source_epsg
        src_wkt = resolve_source_wkt(dataset, source_epsg=request.source_epsg)
        src_nodata = dataset.GetRasterBand(1).GetNoDataValue()
        nodata = resolve_nodata(src_nodata, options)

        log(f"  Dimensoes: {dataset.RasterXSize} x {dataset.RasterYSize}")
        log(f"  Bandas: {dataset.RasterCount}")
        log(f"  EPSG origem: {src_epsg if src_epsg else 'nao identificado'}")
        log(f"  EPSG destino: {options.dst_epsg}")
        log(f"  NoData: {nodata if nodata is not None else 'sem NoData definido'}")

        analysis = analyze_raster_values(dataset, nodata=nodata, options=options)
        log("Diagnostico dos valores raster:")
        log(f"  Dtype origem: {analysis.src_dtype_name}")
        log(f"  Min valido: {analysis.min}")
        log(f"  Max valido: {analysis.max}")
        log(f"  Possui decimais: {analysis.has_decimal}")
        log(f"  Pixels validos lidos: {analysis.valid_pixels_estimated}")
    finally:
        dataset = None

    warp_resampling, overview_resampling = choose_resampling(
        analysis,
        resampling_mode=options.resampling_mode,
    )
    force_float = warp_resampling in ["bilinear", "cubic"]
    out_dtype_name = choose_best_dtype(
        analysis,
        nodata=nodata,
        force_float=force_float,
    )

    log("Decisao automatica raster:")
    log(f"  Dtype saida: {out_dtype_name}")
    log(f"  Warp resampling: {warp_resampling}")
    log(f"  Overview resampling: {overview_resampling}")

    run_translate_or_warp(
        input_raster=input_raster,
        output_raster=output_raster,
        src_wkt=src_wkt,
        src_epsg=src_epsg,
        out_dtype_name=out_dtype_name,
        nodata=nodata,
        warp_resampling=warp_resampling,
        options=options,
    )
    overview_levels = build_internal_overviews(
        output_raster=output_raster,
        dtype_name=out_dtype_name,
        overview_resampling=overview_resampling,
        options=options,
    )

    log(f"Raster otimizado gerado: {output_raster}")
    return RasterOptimizationResult(
        input_raster=str(input_raster),
        output_raster=str(output_raster),
        source_epsg=src_epsg,
        dst_epsg=options.dst_epsg,
        output_dtype=out_dtype_name,
        nodata=nodata,
        warp_resampling=warp_resampling,
        overview_resampling=overview_resampling,
        overview_levels=tuple(overview_levels),
        analysis=analysis,
    )


__all__ = ["build_raster_request", "process_raster_request"]
