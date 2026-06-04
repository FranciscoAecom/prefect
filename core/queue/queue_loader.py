from core.deprecations import warn_deprecated

from core.treatment.queue_loader import (
    QueueRunContext,
    TreatmentQueueRunContext,
    log_empty_queue_diagnostics,
    prepare_treatment_queue,
)


warn_deprecated("core.queue.queue_loader", "core.treatment.queue_loader")


def prepare_processing_queue(*args, **kwargs):
    warn_deprecated("prepare_processing_queue()", "prepare_treatment_queue()")
    return prepare_treatment_queue(*args, **kwargs)


__all__ = [
    "QueueRunContext",
    "TreatmentQueueRunContext",
    "log_empty_queue_diagnostics",
    "prepare_processing_queue",
    "prepare_treatment_queue",
]
