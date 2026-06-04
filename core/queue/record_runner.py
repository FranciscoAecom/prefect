from core.deprecations import warn_deprecated

from core.treatment.record_runner import run_queue_record, run_treatment_record


warn_deprecated("core.queue.record_runner", "core.treatment.record_runner")


__all__ = ["run_queue_record", "run_treatment_record"]
