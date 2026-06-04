import warnings

from core.treatment.queue_loader import (
    QueueRunContext,
    TreatmentQueueRunContext,
    log_empty_queue_diagnostics,
    prepare_treatment_queue,
)


warnings.warn(
    "core.queue.queue_loader esta depreciado; use core.treatment.queue_loader.",
    DeprecationWarning,
    stacklevel=2,
)


def prepare_processing_queue(*args, **kwargs):
    warnings.warn(
        "prepare_processing_queue() esta depreciado; use prepare_treatment_queue().",
        DeprecationWarning,
        stacklevel=2,
    )
    return prepare_treatment_queue(*args, **kwargs)


__all__ = [
    "QueueRunContext",
    "TreatmentQueueRunContext",
    "log_empty_queue_diagnostics",
    "prepare_processing_queue",
    "prepare_treatment_queue",
]
