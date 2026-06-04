from core.deprecations import warn_deprecated

from core.treatment.context_factory import build_treatment_context


warn_deprecated("core.processing.context_factory", "core.treatment.context_factory")


def build_processing_context(*args, **kwargs):
    warn_deprecated("build_processing_context()", "build_treatment_context()")
    return build_treatment_context(*args, **kwargs)


__all__ = ["build_processing_context", "build_treatment_context"]
