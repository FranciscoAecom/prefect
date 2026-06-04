from core.flow.downloads import data_download_flow
from core.flow.pipeline import data_pipeline_flow
from core.flow.pipeline_publish import data_pipeline_publish_flow
from core.flow.publish import data_publish_flow


PREFECT_FLOWS = {
    "data_pipeline": data_pipeline_flow,
    "data_download": data_download_flow,
    "data_publish": data_publish_flow,
    "data_pipeline_publish": data_pipeline_publish_flow,
}


__all__ = [
    "PREFECT_FLOWS",
    "data_download_flow",
    "data_pipeline_flow",
    "data_pipeline_publish_flow",
    "data_publish_flow",
]
