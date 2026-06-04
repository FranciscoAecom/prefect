from core.deprecations import warn_deprecated

from core.treatment.queue_runner import run_treatment_queue


warn_deprecated("core.queue.runner", "core.treatment.queue_runner")


def run_processing_queue(*args, **kwargs):
    warn_deprecated("run_processing_queue()", "run_treatment_queue()")
    return run_treatment_queue(*args, **kwargs)


__all__ = ["run_processing_queue", "run_treatment_queue"]
