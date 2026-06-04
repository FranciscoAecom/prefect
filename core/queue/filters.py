from core.deprecations import warn_deprecated

from core.ingest.filters import QueueFilter


warn_deprecated("core.queue.filters", "core.ingest.filters")


__all__ = ["QueueFilter"]
