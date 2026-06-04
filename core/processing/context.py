import warnings

from core.treatment.context import (
    TreatmentContext,
    TreatmentExecutionContext,
    replace_treatment_context,
)


warnings.warn(
    "core.processing.context esta depreciado; use core.treatment.context.",
    DeprecationWarning,
    stacklevel=2,
)

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
