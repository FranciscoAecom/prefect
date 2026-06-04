from core.metadata import persist_stage_metadata_xmls
from core.treatment.steps.stages import FLOW_STAGE_CREATE_SILVER_XML
from core.sld import persist_stage_slds
from core.utils import log


def persist_silver_artifacts(record, metadata_gdf, persisted_outputs, base_name, persist_dataset, rule_profile):
    if not persisted_outputs:
        return [], []

    log(FLOW_STAGE_CREATE_SILVER_XML)
    xml_paths = persist_stage_metadata_xmls(
        record,
        metadata_gdf,
        [output["path"] for output in persisted_outputs],
        base_name,
        persist_dataset=persist_dataset,
    )
    sld_paths = persist_stage_slds(
        persisted_outputs,
        rule_profile=rule_profile,
        persist_dataset=persist_dataset,
    )
    return xml_paths, sld_paths


__all__ = ["persist_silver_artifacts"]
