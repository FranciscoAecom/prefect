from core.deprecations import warn_deprecated

from core.treatment.issue_report import export_queue_issues_report


warn_deprecated("core.queue.issue_report", "core.treatment.issue_report")


__all__ = ["export_queue_issues_report"]
