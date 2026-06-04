from core.output.consolidation import append_group_consolidated_output
from core.output.paths import build_group_log_path
from core.treatment.dispatcher import (
    process_treatment_record_by_dataset_kind as process_record_by_dataset_kind,
)
from core.utils import clear_context_log, set_context_log


def run_queue_record(
    record,
    output_dir,
    group_state,
    keep_individual_outputs_when_grouping,
):
    record_output_dir = getattr(record, "output_dir", "") or output_dir
    try:
        set_context_log(
            build_group_log_path(record, record_output_dir),
            reset=group_state.should_reset_context_log(record),
        )
        group_state.mark_context_log_started(record)
        record_result = process_record_by_dataset_kind(
            record,
            record_output_dir,
            group_state,
            keep_individual_outputs_when_grouping,
        )
        group_state.register_result(record, record_result)
        if group_state.should_append_consolidated_output(record, record_result):
            append_group_consolidated_output(
                record,
                record_result.final_gdf,
                record_output_dir,
                append=group_state.append_started_for(record),
            )
            group_state.mark_append_started(record)
    finally:
        clear_context_log()
