from core.deprecations import warn_deprecated

from core.treatment.summary import log_queue_summary


warn_deprecated("core.queue.summary", "core.treatment.summary")


__all__ = ["log_queue_summary"]
