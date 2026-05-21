DATA_DOWNLOAD_DEPLOYMENT_NAME = "Download de Dados"
CAR_DOWNLOAD_DEPLOYMENT_NAME = DATA_DOWNLOAD_DEPLOYMENT_NAME
UR_CAR_PROCESSING_DEPLOYMENT_NAME = "CAR - Uso Restrito"
AUTO_INFRACOES_PROCESSING_DEPLOYMENT_NAME = "Autos de Infracao"

DATA_PIPELINE_FLOW_NAME = "Data Pipeline"

CAR_DOWNLOAD_OLD_DEPLOYMENT_NAMES = (
    "CAR - Download",
    "CAR - Uso Restrito - Download",
)
UR_CAR_PROCESSING_OLD_DEPLOYMENT_NAMES = ("CAR - Uso Restrito - Tratamento",)


def qualified_deployment_name(flow_name, deployment_name):
    return f"{flow_name}/{deployment_name}"


def qualified_data_pipeline_deployment_name(deployment_name):
    return qualified_deployment_name(DATA_PIPELINE_FLOW_NAME, deployment_name)


UR_CAR_PROCESSING_QUALIFIED_DEPLOYMENT_NAME = qualified_data_pipeline_deployment_name(
    UR_CAR_PROCESSING_DEPLOYMENT_NAME
)
AUTO_INFRACOES_PROCESSING_QUALIFIED_DEPLOYMENT_NAME = (
    qualified_data_pipeline_deployment_name(AUTO_INFRACOES_PROCESSING_DEPLOYMENT_NAME)
)
UR_CAR_PROCESSING_OLD_QUALIFIED_DEPLOYMENT_NAMES = tuple(
    qualified_data_pipeline_deployment_name(name)
    for name in UR_CAR_PROCESSING_OLD_DEPLOYMENT_NAMES
)


__all__ = [
    "AUTO_INFRACOES_PROCESSING_DEPLOYMENT_NAME",
    "AUTO_INFRACOES_PROCESSING_QUALIFIED_DEPLOYMENT_NAME",
    "CAR_DOWNLOAD_DEPLOYMENT_NAME",
    "CAR_DOWNLOAD_OLD_DEPLOYMENT_NAMES",
    "DATA_DOWNLOAD_DEPLOYMENT_NAME",
    "DATA_PIPELINE_FLOW_NAME",
    "UR_CAR_PROCESSING_DEPLOYMENT_NAME",
    "UR_CAR_PROCESSING_OLD_DEPLOYMENT_NAMES",
    "UR_CAR_PROCESSING_OLD_QUALIFIED_DEPLOYMENT_NAMES",
    "UR_CAR_PROCESSING_QUALIFIED_DEPLOYMENT_NAME",
    "qualified_data_pipeline_deployment_name",
    "qualified_deployment_name",
]
