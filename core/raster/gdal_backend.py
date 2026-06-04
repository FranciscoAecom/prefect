import os
from pathlib import Path

import numpy as np

from core.raster.models import RasterAnalysis, RasterOptimizationOptions
from core.raster.optimization import (
    build_creation_options,
    choose_overview_levels,
    same_as_nodata,
)


GDAL_DTYPE_NAME = {
    "GDT_Byte": "uint8",
    "GDT_UInt16": "uint16",
    "GDT_Int16": "int16",
    "GDT_UInt32": "uint32",
    "GDT_Int32": "int32",
    "GDT_Float32": "float32",
    "GDT_Float64": "float64",
}


def import_gdal():
    try:
        from osgeo import gdal, osr
    except ImportError as exc:
        raise RuntimeError(
            "GDAL/osgeo nao esta disponivel neste ambiente. "
            "Execute o flow raster em um ambiente isolado com GDAL instalado "
            "(por exemplo OSGeo4W ou uma venv/conda especifica para raster)."
        ) from exc

    gdal.UseExceptions()
    return gdal, osr


def configure_gdal(options):
    gdal, _ = import_gdal()
    os.environ.setdefault("GDAL_NUM_THREADS", options.num_threads)
    gdal.SetConfigOption("GDAL_NUM_THREADS", options.num_threads)
    gdal.SetConfigOption("CPL_DEBUG", "OFF")


def gdal_dtype_maps(gdal):
    gdal_to_name = {
        gdal.GDT_Byte: "uint8",
        gdal.GDT_UInt16: "uint16",
        gdal.GDT_Int16: "int16",
        gdal.GDT_UInt32: "uint32",
        gdal.GDT_Int32: "int32",
        gdal.GDT_Float32: "float32",
        gdal.GDT_Float64: "float64",
    }
    name_to_gdal = {
        "uint8": gdal.GDT_Byte,
        "uint16": gdal.GDT_UInt16,
        "int16": gdal.GDT_Int16,
        "uint32": gdal.GDT_UInt32,
        "int32": gdal.GDT_Int32,
        "float32": gdal.GDT_Float32,
        "float64": gdal.GDT_Float64,
    }
    return gdal_to_name, name_to_gdal


def open_raster_readonly(path):
    gdal, _ = import_gdal()
    dataset = gdal.Open(str(path), gdal.GA_ReadOnly)
    if dataset is None:
        raise RuntimeError(f"Nao foi possivel abrir o raster: {path}")
    return dataset


def get_epsg_from_dataset(dataset):
    _, osr = import_gdal()
    projection = dataset.GetProjection()
    if not projection:
        return None

    srs = osr.SpatialReference()
    srs.ImportFromWkt(projection)
    try:
        srs.AutoIdentifyEPSG()
        authority_code = srs.GetAuthorityCode(None)
        return int(authority_code) if authority_code is not None else None
    except (RuntimeError, TypeError, ValueError):
        return None


def resolve_source_wkt(dataset, source_epsg=None):
    _, osr = import_gdal()
    projection = dataset.GetProjection()
    if projection:
        return projection
    if source_epsg is None:
        raise ValueError(
            "Raster sem CRS/projecao no metadado. Informe source_epsg para reprojetar."
        )

    srs = osr.SpatialReference()
    srs.ImportFromEPSG(int(source_epsg))
    return srs.ExportToWkt()


def analyze_raster_values(dataset, nodata, options):
    gdal, _ = import_gdal()
    gdal_to_name, _ = gdal_dtype_maps(gdal)
    global_min = None
    global_max = None
    has_decimal = False
    valid_pixels_estimated = 0
    src_gdal_dtype = dataset.GetRasterBand(1).DataType
    src_dtype_name = gdal_to_name.get(src_gdal_dtype, f"GDAL_{src_gdal_dtype}")

    width = dataset.RasterXSize
    height = dataset.RasterYSize
    bands = dataset.RasterCount

    for band_index in range(1, bands + 1):
        band = dataset.GetRasterBand(band_index)
        for yoff in range(0, height, options.block_size):
            ysize = min(options.block_size, height - yoff)
            for xoff in range(0, width, options.block_size):
                xsize = min(options.block_size, width - xoff)
                arr = band.ReadAsArray(xoff, yoff, xsize, ysize)
                if arr is None:
                    continue

                if np.issubdtype(arr.dtype, np.floating):
                    valid = np.isfinite(arr)
                else:
                    valid = np.ones(arr.shape, dtype=bool)

                if nodata is not None:
                    valid &= ~same_as_nodata(arr, nodata)

                if not np.any(valid):
                    continue

                vals = arr[valid]
                valid_pixels_estimated += vals.size

                local_min = float(np.min(vals))
                local_max = float(np.max(vals))
                global_min = local_min if global_min is None else min(global_min, local_min)
                global_max = local_max if global_max is None else max(global_max, local_max)

                if np.issubdtype(vals.dtype, np.floating):
                    frac = np.abs(vals - np.round(vals))
                    if np.any(frac > options.decimal_tolerance):
                        has_decimal = True

    if global_min is None or global_max is None:
        raise RuntimeError("Nao foi possivel calcular min/max: raster sem pixels validos.")

    return RasterAnalysis(
        min=global_min,
        max=global_max,
        has_decimal=has_decimal,
        src_dtype_name=src_dtype_name,
        valid_pixels_estimated=int(valid_pixels_estimated),
    )


def run_translate_or_warp(
    input_raster,
    output_raster,
    src_wkt,
    src_epsg,
    out_dtype_name,
    nodata,
    warp_resampling,
    options,
):
    gdal, _ = import_gdal()
    _, name_to_gdal = gdal_dtype_maps(gdal)
    output_raster = Path(output_raster)
    output_raster.parent.mkdir(parents=True, exist_ok=True)
    if output_raster.exists():
        output_raster.unlink()

    creation_options = build_creation_options(out_dtype_name, options)
    out_gdal_dtype = name_to_gdal[out_dtype_name]

    if src_epsg == options.dst_epsg:
        kwargs = {
            "format": "GTiff",
            "outputType": out_gdal_dtype,
            "creationOptions": creation_options,
            "outputSRS": f"EPSG:{options.dst_epsg}",
        }
        if nodata is not None:
            kwargs["noData"] = nodata
        translate_options = gdal.TranslateOptions(**kwargs)
        result = gdal.Translate(str(output_raster), str(input_raster), options=translate_options)
    else:
        kwargs = {
            "format": "GTiff",
            "srcSRS": src_wkt,
            "dstSRS": f"EPSG:{options.dst_epsg}",
            "outputType": out_gdal_dtype,
            "resampleAlg": warp_resampling,
            "multithread": True,
            "creationOptions": creation_options,
            "warpOptions": [f"NUM_THREADS={options.num_threads}"],
        }
        if nodata is not None:
            kwargs["srcNodata"] = nodata
            kwargs["dstNodata"] = nodata
        warp_options = gdal.WarpOptions(**kwargs)
        result = gdal.Warp(str(output_raster), str(input_raster), options=warp_options)

    if result is None:
        raise RuntimeError("GDAL nao retornou dataset de saida. A escrita falhou.")

    result.FlushCache()
    result = None


def build_internal_overviews(output_raster, dtype_name, overview_resampling, options):
    gdal, _ = import_gdal()
    dataset = gdal.Open(str(output_raster), gdal.GA_Update)
    if dataset is None:
        raise RuntimeError(f"Nao foi possivel abrir saida para overviews: {output_raster}")

    levels = choose_overview_levels(dataset.RasterXSize, dataset.RasterYSize)
    if not levels:
        dataset = None
        return []

    predictor = "3" if dtype_name in ["float32", "float64"] else "2"
    gdal.SetConfigOption("COMPRESS_OVERVIEW", options.compress)
    gdal.SetConfigOption("PREDICTOR_OVERVIEW", predictor)
    gdal.SetConfigOption("BIGTIFF_OVERVIEW", options.bigtiff)
    gdal.SetConfigOption("GDAL_TIFF_OVR_BLOCKSIZE", str(options.block_size))

    dataset.BuildOverviews(overview_resampling.upper(), levels)
    dataset.FlushCache()
    dataset = None
    return levels
