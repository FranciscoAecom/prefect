from core.deprecations import warn_deprecated

from core.treatment.record_processor import process_treatment_record
from core.treatment.result import TreatmentRecordResult


warn_deprecated("core.processing.record_processor", "core.treatment.record_processor")

ProcessRecordResult = TreatmentRecordResult


def process_record(*args, **kwargs):
    warn_deprecated("process_record()", "process_treatment_record()")
    return process_treatment_record(*args, **kwargs)


__all__ = [
    "ProcessRecordResult",
    "TreatmentRecordResult",
    "process_record",
    "process_treatment_record",
]
