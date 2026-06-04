import warnings

from core.treatment.summary import log_queue_summary


warnings.warn(
    "core.queue.summary esta depreciado; use core.treatment.summary.",
    DeprecationWarning,
    stacklevel=2,
)


__all__ = ["log_queue_summary"]
