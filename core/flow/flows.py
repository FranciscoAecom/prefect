from core.flow.downloads import data_download_flow
from core.flow.treatment import data_treatment_flow
from core.flow.publish import data_publish_flow


PREFECT_FLOWS = {
    "data_download": data_download_flow,
    "data_treatment": data_treatment_flow,
    "data_publish": data_publish_flow,
}


__all__ = [
    "PREFECT_FLOWS",
    "data_download_flow",
    "data_treatment_flow",
    "data_publish_flow",
]
