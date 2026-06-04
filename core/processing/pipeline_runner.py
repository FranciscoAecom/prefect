import warnings

from core.treatment.steps_runner import run_treatment_steps


warnings.warn(
    "core.processing.pipeline_runner esta depreciado; use core.treatment.steps_runner.",
    DeprecationWarning,
    stacklevel=2,
)


def run_processing_pipeline(*args, **kwargs):
    warnings.warn(
        "run_processing_pipeline() esta depreciado; use run_treatment_steps().",
        DeprecationWarning,
        stacklevel=2,
    )
    return run_treatment_steps(*args, **kwargs)


__all__ = ["run_processing_pipeline", "run_treatment_steps"]
