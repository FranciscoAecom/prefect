import warnings

from core.treatment.settings import QueueRunSettings


warnings.warn(
    "core.queue.settings esta depreciado; use core.treatment.settings.",
    DeprecationWarning,
    stacklevel=2,
)


__all__ = ["QueueRunSettings"]
