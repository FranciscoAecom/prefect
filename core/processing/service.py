from core.deprecations import warn_deprecated

from core.treatment.service import TreatmentService


warn_deprecated("core.processing.service", "core.treatment.service")

ProcessingService = TreatmentService


__all__ = ["ProcessingService", "TreatmentService"]
