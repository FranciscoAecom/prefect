from core.ingest.dataset_types import DATASET_KIND_RASTER
from core.treatment.handlers.raster import process_raster_treatment_record
from core.treatment.handlers.vector import process_vector_treatment_record


def process_treatment_record_by_dataset_kind(
    record,
    output_dir,
    group_state,
    keep_individual_outputs_when_grouping,
):
    if getattr(record, "dataset_kind", "") == DATASET_KIND_RASTER:
        return process_raster_treatment_record(
            record,
            output_dir,
            use_configured_final_name=group_state.use_configured_final_name(record),
        )

    return process_vector_treatment_record(
        record,
        output_dir,
        id_start=group_state.id_start_for(record),
        use_configured_final_name=group_state.use_configured_final_name(record),
        persist_individual_output=group_state.persist_individual_output(
            record,
            keep_individual_outputs_when_grouping,
        ),
    )


__all__ = ["process_treatment_record_by_dataset_kind"]
