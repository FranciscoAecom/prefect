from dataclasses import dataclass, field
from pathlib import Path


@dataclass(frozen=True)
class RasterOptimizationOptions:
    dst_epsg: int = 4326
    block_size: int = 512
    compress: str = "LZW"
    bigtiff: str = "IF_SAFER"
    num_threads: str = "ALL_CPUS"
    decimal_tolerance: float = 1e-6
    nodata_mode: str = "auto"
    custom_nodata: float | None = None
    resampling_mode: str = "auto"


@dataclass(frozen=True)
class RasterOptimizationRequest:
    input_raster: Path
    output_raster: Path
    source_epsg: int | None = None
    options: RasterOptimizationOptions = field(default_factory=RasterOptimizationOptions)


@dataclass(frozen=True)
class RasterAnalysis:
    min: float
    max: float
    has_decimal: bool
    src_dtype_name: str
    valid_pixels_estimated: int


@dataclass(frozen=True)
class RasterOptimizationResult:
    input_raster: str
    output_raster: str
    source_epsg: int | None
    dst_epsg: int
    output_dtype: str
    nodata: float | None
    warp_resampling: str
    overview_resampling: str
    overview_levels: tuple[int, ...]
    analysis: RasterAnalysis
