from core.deprecations import warn_deprecated

from core.treatment.settings import QueueRunSettings


warn_deprecated("core.queue.settings", "core.treatment.settings")


__all__ = ["QueueRunSettings"]
