from core.config.settings import APP_SETTINGS

PROJECT_ROOT = APP_SETTINGS.paths.project_root
DATA_LAKE_BASE = APP_SETTINGS.paths.data_lake_base
DATA_LAKE_TEMP_STAGE = APP_SETTINGS.paths.data_lake_temp_stage
DATA_LAKE_BRONZE_STAGE = APP_SETTINGS.paths.data_lake_bronze_stage
DATA_LAKE_SILVER_STAGE = APP_SETTINGS.paths.data_lake_silver_stage

INGEST_WORKBOOK_PATH = APP_SETTINGS.paths.ingest_workbook_path
INGEST_SHEET_NAME = APP_SETTINGS.paths.ingest_sheet_name
DICTIONARIES_SHEET_NAME = APP_SETTINGS.paths.dictionaries_sheet_name
INGEST_DOWNLOAD_STATUS = APP_SETTINGS.ingest.download_status
INGEST_TREATMENT_STATUS = APP_SETTINGS.ingest.treatment_status
INGEST_PUBLISH_STATUS = APP_SETTINGS.ingest.publish_status
INGEST_TREATMENT_STATUSES = APP_SETTINGS.ingest.treatment_statuses
INGEST_PROCESSING_STATUSES = INGEST_TREATMENT_STATUSES

OUTPUT_BASE = APP_SETTINGS.paths.output_base

CAR_PUBLIC_API_BASE = APP_SETTINGS.downloads.car_public_api_base
DOWNLOAD_ARCHIVE_BASE = APP_SETTINGS.downloads.archive_base
DOWNLOAD_EXTRACT_BASE = APP_SETTINGS.downloads.extract_base
CAR_DOWNLOAD_EXTRACT_BASE = DOWNLOAD_EXTRACT_BASE

RULES_BASE = APP_SETTINGS.paths.rules_base
DEFAULT_RULE_PROFILE = APP_SETTINGS.default_rule_profile

REQUIRES_PYTHON = APP_SETTINGS.treatment.requires_python

BATCH_SIZE = APP_SETTINGS.treatment.batch_size
SPATIAL_TRANSFORM_CHUNK_SIZE = APP_SETTINGS.treatment.spatial_transform_chunk_size

CRS_WGS84 = APP_SETTINGS.treatment.crs_wgs84
CRS_EQUAL_AREA = APP_SETTINGS.treatment.crs_equal_area
DEFAULT_INPUT_CRS = APP_SETTINGS.treatment.default_input_crs

ID_FIELD = APP_SETTINGS.treatment.id_field
AREA_FIELD = APP_SETTINGS.treatment.area_field
PERIMETER_FIELD = APP_SETTINGS.treatment.perimeter_field
LONGITUDE_FIELD = APP_SETTINGS.treatment.longitude_field
LATITUDE_FIELD = APP_SETTINGS.treatment.latitude_field

GEOM_DUPLICATES_LAYER = APP_SETTINGS.quality.geom_duplicates_layer
OGC_INVALID_LAYER = APP_SETTINGS.quality.ogc_invalid_layer
OGC_REASON_FIELD = APP_SETTINGS.quality.ogc_reason_field

ENABLE_ATTRIBUTE_DUPLICATE_REPORT = APP_SETTINGS.quality.enable_attribute_duplicate_report
ENABLE_GEOMETRIC_DUPLICATE_REPORT = APP_SETTINGS.quality.enable_geometric_duplicate_report
ENABLE_OGC_INVALID_REPORT = APP_SETTINGS.quality.enable_ogc_invalid_report
EXPORT_OUTPUT_QUALITY_REPORT_FILES = APP_SETTINGS.quality.export_output_quality_report_files
ENABLE_GROUP_CONSOLIDATION = APP_SETTINGS.quality.enable_group_consolidation
KEEP_INDIVIDUAL_OUTPUTS_WHEN_GROUPING = (
    APP_SETTINGS.quality.keep_individual_outputs_when_grouping
)

USE_ARROW_IO = APP_SETTINGS.treatment.use_arrow_io
INTERACTIVE_ATTRIBUTE_REVIEW = APP_SETTINGS.treatment.interactive_attribute_review
