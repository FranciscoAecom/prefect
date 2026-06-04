import warnings

from core.treatment.steps.bronze_step import *


warnings.warn(
    "core.processing.bronze_step esta depreciado; use core.treatment.steps.bronze_step.",
    DeprecationWarning,
    stacklevel=2,
)
