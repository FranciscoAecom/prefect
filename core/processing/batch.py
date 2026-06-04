import warnings

from core.treatment.steps.batch import *


warnings.warn(
    "core.processing.batch esta depreciado; use core.treatment.steps.batch.",
    DeprecationWarning,
    stacklevel=2,
)
