import warnings

from core.treatment.steps.events import *


warnings.warn(
    "core.processing.events esta depreciado; use core.treatment.steps.events.",
    DeprecationWarning,
    stacklevel=2,
)
