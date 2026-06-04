import warnings

from core.treatment.result import (
    TreatmentRecordResult,
    treatment_failure_result,
    treatment_success_result,
)


warnings.warn(
    "core.processing.result esta depreciado; use core.treatment.result.",
    DeprecationWarning,
    stacklevel=2,
)

ProcessRecordResult = TreatmentRecordResult


def failure_result():
    warnings.warn(
        "failure_result() esta depreciado; use treatment_failure_result().",
        DeprecationWarning,
        stacklevel=2,
    )
    return treatment_failure_result()


def success_result(context):
    warnings.warn(
        "success_result() esta depreciado; use treatment_success_result().",
        DeprecationWarning,
        stacklevel=2,
    )
    return treatment_success_result(context)


__all__ = [
    "ProcessRecordResult",
    "TreatmentRecordResult",
    "failure_result",
    "success_result",
    "treatment_failure_result",
    "treatment_success_result",
]
