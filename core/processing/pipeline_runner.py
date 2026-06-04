from core.deprecations import warn_deprecated

from core.treatment.steps_runner import run_treatment_steps


warn_deprecated("core.processing.pipeline_runner", "core.treatment.steps_runner")


def run_processing_pipeline(*args, **kwargs):
    warn_deprecated("run_processing_pipeline()", "run_treatment_steps()")
    return run_treatment_steps(*args, **kwargs)


__all__ = ["run_processing_pipeline", "run_treatment_steps"]
