import math

import numpy as np

from core.raster.models import RasterAnalysis, RasterOptimizationOptions


def same_as_nodata(arr, nodata):
    if nodata is None:
        return np.zeros(arr.shape, dtype=bool)
    if isinstance(nodata, float) and math.isnan(nodata):
        return np.isnan(arr)
    return arr == nodata


def value_fits_dtype(value, dtype_name):
    if value is None:
        return True

    if dtype_name == "float32":
        return np.isfinite(value) and abs(value) <= np.finfo(np.float32).max
    if dtype_name == "float64":
        return True

    if not float(value).is_integer():
        return False

    info = np.iinfo(np.dtype(dtype_name))
    return info.min <= int(value) <= info.max


def choose_best_dtype(analysis, nodata=None, force_float=False):
    if analysis.has_decimal or force_float:
        if value_fits_dtype(nodata, "float32"):
            return "float32"
        return "float64"

    min_i = int(math.floor(analysis.min))
    max_i = int(math.ceil(analysis.max))

    candidates = []
    if min_i >= 0:
        candidates.extend(["uint8", "uint16", "uint32"])
    candidates.extend(["int16", "int32"])

    for dtype_name in candidates:
        info = np.iinfo(np.dtype(dtype_name))
        if info.min <= min_i <= info.max and info.min <= max_i <= info.max:
            if value_fits_dtype(nodata, dtype_name):
                return dtype_name

    return "float32" if value_fits_dtype(nodata, "float32") else "float64"


def choose_overview_levels(width, height):
    max_dim = max(width, height)

    if max_dim <= 1024:
        return []
    if max_dim <= 4096:
        return [2, 4]

    levels = []
    level = 2
    while (max_dim / level) > 512 and len(levels) < 8:
        levels.append(level)
        level *= 2

    if len(levels) < 3 and max_dim > 4096:
        for level in [2, 4, 8]:
            if level not in levels:
                levels.append(level)

    return sorted(set(levels))


def choose_resampling(analysis, resampling_mode="auto"):
    if analysis.has_decimal:
        default_warp_resampling = "bilinear"
        default_overview_resampling = "average"
    else:
        default_warp_resampling = "near"
        default_overview_resampling = "nearest"

    if resampling_mode == "auto":
        return default_warp_resampling, default_overview_resampling
    if resampling_mode == "near":
        return "near", "nearest"
    return resampling_mode, "average"


def resolve_nodata(src_nodata, options):
    if options.nodata_mode == "auto":
        return src_nodata
    if options.nodata_mode == "none":
        return None
    if options.nodata_mode == "custom":
        return options.custom_nodata
    raise ValueError(f"Modo NoData nao suportado: {options.nodata_mode}")


def build_creation_options(dtype_name, options):
    predictor = "3" if dtype_name in ["float32", "float64"] else "2"
    return [
        "TILED=YES",
        f"BLOCKXSIZE={options.block_size}",
        f"BLOCKYSIZE={options.block_size}",
        f"COMPRESS={options.compress}",
        f"PREDICTOR={predictor}",
        f"BIGTIFF={options.bigtiff}",
        f"NUM_THREADS={options.num_threads}",
    ]


def coerce_analysis(analysis):
    if isinstance(analysis, RasterAnalysis):
        return analysis
    return RasterAnalysis(**analysis)
