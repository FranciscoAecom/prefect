import warnings

from core.treatment.record_runner import run_queue_record, run_treatment_record


warnings.warn(
    "core.queue.record_runner esta depreciado; use core.treatment.record_runner.",
    DeprecationWarning,
    stacklevel=2,
)


__all__ = ["run_queue_record", "run_treatment_record"]
