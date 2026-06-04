import warnings

from core.treatment.issue_report import export_queue_issues_report


warnings.warn(
    "core.queue.issue_report esta depreciado; use core.treatment.issue_report.",
    DeprecationWarning,
    stacklevel=2,
)


__all__ = ["export_queue_issues_report"]
