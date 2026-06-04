import warnings

from core.treatment.steps.errors import *


warnings.warn(
    "core.processing.errors esta depreciado; use core.treatment.steps.errors.",
    DeprecationWarning,
    stacklevel=2,
)
