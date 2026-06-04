import warnings

from core.treatment.queue_runner import run_treatment_queue


warnings.warn(
    "core.queue.runner esta depreciado; use core.treatment.queue_runner.",
    DeprecationWarning,
    stacklevel=2,
)


def run_processing_queue(*args, **kwargs):
    warnings.warn(
        "run_processing_queue() esta depreciado; use run_treatment_queue().",
        DeprecationWarning,
        stacklevel=2,
    )
    return run_treatment_queue(*args, **kwargs)


__all__ = ["run_processing_queue", "run_treatment_queue"]
