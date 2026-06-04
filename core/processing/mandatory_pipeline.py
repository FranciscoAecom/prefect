import warnings

from core.treatment.steps.mandatory_pipeline import *


warnings.warn(
    "core.processing.mandatory_pipeline esta depreciado; use core.treatment.steps.mandatory_pipeline.",
    DeprecationWarning,
    stacklevel=2,
)
