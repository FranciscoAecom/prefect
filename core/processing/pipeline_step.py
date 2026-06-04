import warnings

from core.treatment.steps.pipeline_step import *


warnings.warn(
    "core.processing.pipeline_step esta depreciado; use core.treatment.steps.pipeline_step.",
    DeprecationWarning,
    stacklevel=2,
)
