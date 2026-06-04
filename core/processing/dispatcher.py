from core.ingest.dataset_types import DATASET_KIND_RASTER
from core.processing.record_processor import process_record
from core.raster.record_processor import process_raster_record


def process_record_by_dataset_kind(
    record,
    output_dir,
    group_state,
    keep_individual_outputs_when_grouping,
):
    if getattr(record, "dataset_kind", "") == DATASET_KIND_RASTER:
        return process_raster_record(
            record,
            output_dir,
            use_configured_final_name=group_state.use_configured_final_name(record),
        )

    return process_record(
        record,
        output_dir,
        id_start=group_state.id_start_for(record),
        use_configured_final_name=group_state.use_configured_final_name(record),
        persist_individual_output=group_state.persist_individual_output(
            record,
            keep_individual_outputs_when_grouping,
        ),
    )


__all__ = ["process_record_by_dataset_kind"]
