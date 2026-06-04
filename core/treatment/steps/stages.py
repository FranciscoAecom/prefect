FLOW_STAGE_READ_TEMP = "Etapa 1/7 - Ler arquivo no temp"
FLOW_STAGE_COPY_BRONZE = "Etapa 2/7 - Copiando arquivo bruto do temp para bronze"
FLOW_STAGE_BRONZE_AND_XML = "Etapa 2/7 a 4/7 - Bronze e XML do bronze"
FLOW_STAGE_CREATE_BRONZE_XML = "Etapa 3/7 - Criando XML do bronze"
FLOW_STAGE_SAVE_BRONZE_XML = "Etapa 4/7 - XML do bronze salvo"
FLOW_STAGE_TREATMENTS = "Etapa 5/7 - Fazer tratamentos"
FLOW_STAGE_SAVE_SILVER = "Etapa 6/7 - Salvando dado tratado no silver"
FLOW_STAGE_SILVER_AND_XML = "Etapa 6/7 e 7/7 - Salvar silver e XML do silver"
FLOW_STAGE_CREATE_SILVER_XML = "Etapa 7/7 - Criando XML do silver"


def stage_message(stage, message):
    return f"{stage}: {message}"


__all__ = [
    "FLOW_STAGE_BRONZE_AND_XML",
    "FLOW_STAGE_COPY_BRONZE",
    "FLOW_STAGE_CREATE_BRONZE_XML",
    "FLOW_STAGE_CREATE_SILVER_XML",
    "FLOW_STAGE_READ_TEMP",
    "FLOW_STAGE_SAVE_BRONZE_XML",
    "FLOW_STAGE_SAVE_SILVER",
    "FLOW_STAGE_SILVER_AND_XML",
    "FLOW_STAGE_TREATMENTS",
    "stage_message",
]
