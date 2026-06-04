import warnings

from core.treatment.context_factory import build_treatment_context


warnings.warn(
    "core.processing.context_factory esta depreciado; use core.treatment.context_factory.",
    DeprecationWarning,
    stacklevel=2,
)


def build_processing_context(*args, **kwargs):
    warnings.warn(
        "build_processing_context() esta depreciado; use build_treatment_context().",
        DeprecationWarning,
        stacklevel=2,
    )
    return build_treatment_context(*args, **kwargs)


__all__ = ["build_processing_context", "build_treatment_context"]
