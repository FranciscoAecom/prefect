from dataclasses import dataclass
import os
from pathlib import Path

from core.config.defaults import (
    DEFAULT_CAR_PUBLIC_API_BASE,
    DEFAULT_DATA_LAKE_BASE,
    DEFAULT_DOWNLOAD_ARCHIVE_BASE,
    DEFAULT_DOWNLOAD_EXTRACT_BASE,
)


@dataclass(frozen=True)
class PathSettings:
    project_root: Path = Path(__file__).resolve().parents[2]
    data_lake_temp_stage: str = "temp"
    data_lake_bronze_stage: str = "bronze_data"
    data_lake_silver_stage: str = "silver_data"
    ingest_sheet_name: str = "datas"
    dictionaries_sheet_name: str = "dictionaries"
    rules_folder: str = "rules"
    input_workbook_name: str = "st_Ingest_parameter.xlsx"

    @property
    def data_lake_base(self):
        return Path(os.getenv("DATA_LAKE_BASE", DEFAULT_DATA_LAKE_BASE))

    @property
    def ingest_workbook_path(self):
        return self.project_root / "input" / self.input_workbook_name

    @property
    def output_base(self):
        return self.data_lake_base

    @property
    def rules_base(self):
        return self.project_root / self.rules_folder


@dataclass(frozen=True)
class IngestSettings:
    download_status: str = "download"
    treatment_status: str = "treatment"
    publish_status: str = "publish"

    @property
    def treatment_statuses(self):
        return (self.treatment_status,)


@dataclass(frozen=True)
class DownloadSettings:
    car_public_api_base: str = DEFAULT_CAR_PUBLIC_API_BASE
    archive_base: str = DEFAULT_DOWNLOAD_ARCHIVE_BASE
    extract_base: str = DEFAULT_DOWNLOAD_EXTRACT_BASE


@dataclass(frozen=True)
class TreatmentSettings:
    requires_python: str = ">=3.14"
    batch_size: int = 50000
    spatial_transform_chunk_size: int = 5000
    crs_wgs84: str = "EPSG:4326"
    crs_equal_area: str = "EPSG:5880"
    default_input_crs: str = "EPSG:4674"
    id_field: str = "acm_id"
    area_field: str = "acm_a_ha"
    perimeter_field: str = "acm_prm_km"
    longitude_field: str = "acm_long"
    latitude_field: str = "acm_lat"
    use_arrow_io: bool = True
    interactive_attribute_review: bool = False


@dataclass(frozen=True)
class QualitySettings:
    geom_duplicates_layer: str = "duplicados_geometrias"
    ogc_invalid_layer: str = "geometrias_invalidas_ogc"
    ogc_reason_field: str = "ogc_motivo"
    enable_attribute_duplicate_report: bool = True
    enable_geometric_duplicate_report: bool = True
    enable_ogc_invalid_report: bool = True
    export_output_quality_report_files: bool = True
    enable_group_consolidation: bool = False
    keep_individual_outputs_when_grouping: bool = False


@dataclass(frozen=True)
class AppSettings:
    paths: PathSettings = PathSettings()
    ingest: IngestSettings = IngestSettings()
    downloads: DownloadSettings = DownloadSettings()
    treatment: TreatmentSettings = TreatmentSettings()
    quality: QualitySettings = QualitySettings()
    default_rule_profile: str = "default"


APP_SETTINGS = AppSettings()
