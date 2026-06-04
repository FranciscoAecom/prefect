from core.deprecations import warn_deprecated

from core.treatment.result import (
    TreatmentRecordResult,
    treatment_failure_result,
    treatment_success_result,
)


warn_deprecated("core.processing.result", "core.treatment.result")

ProcessRecordResult = TreatmentRecordResult


def failure_result():
    warn_deprecated("failure_result()", "treatment_failure_result()")
    return treatment_failure_result()


def success_result(context):
    warn_deprecated("success_result()", "treatment_success_result()")
    return treatment_success_result(context)


__all__ = [
    "ProcessRecordResult",
    "TreatmentRecordResult",
    "failure_result",
    "success_result",
    "treatment_failure_result",
    "treatment_success_result",
]
