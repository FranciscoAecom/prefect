from pathlib import Path

from core.bronze import ensure_bronze_dataset
from core.metadata.xml import load_dictionary_descriptions, persist_bronze_metadata_xml
from core.output.naming import build_final_output_base_name
from core.processing.context import replace_context
from core.processing.stages import (
    FLOW_STAGE_COPY_BRONZE,
    FLOW_STAGE_CREATE_BRONZE_XML,
    FLOW_STAGE_SAVE_BRONZE_XML,
    stage_message,
)
from core.utils import log


def persist_bronze_step(context, use_configured_final_name=False):
    log(FLOW_STAGE_COPY_BRONZE)
    bronze_dataset_path = ensure_bronze_dataset(context.record)
    if not bronze_dataset_path:
        log(
            stage_message(
                FLOW_STAGE_COPY_BRONZE,
                "bronze nao gerado porque nao foi encontrado dado bruto elegivel",
            )
        )
        return context

    log(
        stage_message(
            FLOW_STAGE_COPY_BRONZE,
            f"arquivo bruto preservado no bronze: {bronze_dataset_path}",
        )
    )
    log(FLOW_STAGE_CREATE_BRONZE_XML)
    base_name = build_bronze_metadata_base_name(context, use_configured_final_name)
    xml_path = persist_bronze_metadata_xml(
        context.record,
        bronze_dataset_path,
        load_dictionary_descriptions(),
        base_name,
    )
    if xml_path:
        log(stage_message(FLOW_STAGE_SAVE_BRONZE_XML, str(xml_path)))
    return replace_context(context, bronze_dataset_path=str(bronze_dataset_path))


def build_bronze_metadata_base_name(context, use_configured_final_name=False):
    if use_configured_final_name:
        return build_final_output_base_name(context.record)
    return f"{Path(context.record.input_path).stem}_validado"


__all__ = ["persist_bronze_step"]
