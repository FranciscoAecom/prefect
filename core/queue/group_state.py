import warnings

from core.treatment.group_state import QueueGroupState


warnings.warn(
    "core.queue.group_state esta depreciado; use core.treatment.group_state.",
    DeprecationWarning,
    stacklevel=2,
)


__all__ = ["QueueGroupState"]
