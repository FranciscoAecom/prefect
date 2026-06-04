from core.output.columns import drop_internal_output_columns
from core.output.consolidation import append_group_consolidated_output
from core.output.identifiers import assign_output_identifiers
from core.output.naming import (
    build_final_output_base_name,
    build_theme_output_dir,
    resolve_output_name_template,
    resolve_output_reference_date,
    sanitize_output_name,
)
from core.output.paths import (
    build_group_log_path,
    build_treatment_group_key,
)
from core.output.quality import (
    OutputQualityConfig,
    OutputQualitySummary,
    build_output_quality_summary,
    log_output_quality_summary,
)


def __getattr__(name):
    if name == "save_outputs":
        from core.silver import save_outputs

        return save_outputs
    raise AttributeError(name)

__all__ = [
    "OutputQualitySummary",
    "OutputQualityConfig",
    "append_group_consolidated_output",
    "assign_output_identifiers",
    "build_group_log_path",
    "build_treatment_group_key",
    "build_final_output_base_name",
    "build_output_quality_summary",
    "build_theme_output_dir",
    "drop_internal_output_columns",
    "log_output_quality_summary",
    "resolve_output_name_template",
    "resolve_output_reference_date",
    "save_outputs",
    "sanitize_output_name",
]
