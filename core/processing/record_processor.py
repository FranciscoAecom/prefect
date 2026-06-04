import warnings

from core.treatment.record_processor import process_treatment_record
from core.treatment.result import TreatmentRecordResult


warnings.warn(
    "core.processing.record_processor esta depreciado; use core.treatment.record_processor.",
    DeprecationWarning,
    stacklevel=2,
)

ProcessRecordResult = TreatmentRecordResult


def process_record(*args, **kwargs):
    warnings.warn(
        "process_record() esta depreciado; use process_treatment_record().",
        DeprecationWarning,
        stacklevel=2,
    )
    return process_treatment_record(*args, **kwargs)


__all__ = [
    "ProcessRecordResult",
    "TreatmentRecordResult",
    "process_record",
    "process_treatment_record",
]
