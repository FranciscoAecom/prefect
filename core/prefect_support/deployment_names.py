DATA_DOWNLOAD_DEPLOYMENT_NAME = "Download de Dados"
DATA_PUBLISH_DEPLOYMENT_NAME = "Publish GeoServer GeoNetwork"
CAR_DOWNLOAD_DEPLOYMENT_NAME = DATA_DOWNLOAD_DEPLOYMENT_NAME
SCHEDULED_TREATMENT_DEPLOYMENT_NAME = "Treatment Agendado pela Ingest"

DATA_TREATMENT_FLOW_NAME = "Data Treatment"
DATA_PUBLISH_FLOW_NAME = "Data Publish"


def qualified_deployment_name(flow_name, deployment_name):
    return f"{flow_name}/{deployment_name}"


def qualified_data_treatment_deployment_name(deployment_name):
    return qualified_deployment_name(DATA_TREATMENT_FLOW_NAME, deployment_name)


def qualified_data_publish_deployment_name(deployment_name):
    return qualified_deployment_name(DATA_PUBLISH_FLOW_NAME, deployment_name)


SCHEDULED_TREATMENT_QUALIFIED_DEPLOYMENT_NAME = (
    qualified_data_treatment_deployment_name(SCHEDULED_TREATMENT_DEPLOYMENT_NAME)
)


__all__ = [
    "CAR_DOWNLOAD_DEPLOYMENT_NAME",
    "DATA_DOWNLOAD_DEPLOYMENT_NAME",
    "DATA_PUBLISH_DEPLOYMENT_NAME",
    "DATA_PUBLISH_FLOW_NAME",
    "DATA_TREATMENT_FLOW_NAME",
    "SCHEDULED_TREATMENT_DEPLOYMENT_NAME",
    "SCHEDULED_TREATMENT_QUALIFIED_DEPLOYMENT_NAME",
    "qualified_data_publish_deployment_name",
    "qualified_data_treatment_deployment_name",
    "qualified_deployment_name",
]
