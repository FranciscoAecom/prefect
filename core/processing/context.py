from core.deprecations import warn_deprecated

from core.treatment.context import (
    TreatmentContext,
    TreatmentExecutionContext,
    replace_treatment_context,
)


warn_deprecated("core.processing.context", "core.treatment.context")

ProcessingContext = TreatmentContext
ProcessingExecutionContext = TreatmentExecutionContext
replace_context = replace_treatment_context


__all__ = [
    "ProcessingContext",
    "ProcessingExecutionContext",
    "TreatmentContext",
    "TreatmentExecutionContext",
    "replace_context",
    "replace_treatment_context",
]
