import warnings

from core.treatment.service import TreatmentService


warnings.warn(
    "core.processing.service esta depreciado; use core.treatment.service.",
    DeprecationWarning,
    stacklevel=2,
)

ProcessingService = TreatmentService


__all__ = ["ProcessingService", "TreatmentService"]
