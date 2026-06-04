import warnings

from core.treatment.steps.postprocess_functions import *


warnings.warn(
    "core.processing.postprocess_functions esta depreciado; use core.treatment.steps.postprocess_functions.",
    DeprecationWarning,
    stacklevel=2,
)
