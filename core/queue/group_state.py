from core.deprecations import warn_deprecated

from core.treatment.group_state import QueueGroupState


warn_deprecated("core.queue.group_state", "core.treatment.group_state")


__all__ = ["QueueGroupState"]
