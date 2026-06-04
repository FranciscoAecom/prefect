import warnings

from core.treatment.steps.postprocess_step import *


warnings.warn(
    "core.processing.postprocess_step esta depreciado; use core.treatment.steps.postprocess_step.",
    DeprecationWarning,
    stacklevel=2,
)
