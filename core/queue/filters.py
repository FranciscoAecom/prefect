import warnings

from core.ingest.filters import QueueFilter


warnings.warn(
    "core.queue.filters esta depreciado; use core.ingest.filters.",
    DeprecationWarning,
    stacklevel=2,
)


__all__ = ["QueueFilter"]
