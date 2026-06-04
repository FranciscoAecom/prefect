from dataclasses import dataclass, field

from core.utils import log


@dataclass(frozen=True)
class TreatmentError(Exception):
    code: str
    message: str
    details: dict = field(default_factory=dict)

    def __str__(self):
        return self.message


def input_error(message, **details):
    return TreatmentError("input_error", message, details)


def schema_error(message, **details):
    return TreatmentError("schema_error", message, details)


def rule_error(message, **details):
    return TreatmentError("rule_error", message, details)


def output_error(message, **details):
    return TreatmentError("output_error", message, details)


def log_treatment_error(prefix, exc):
    if isinstance(exc, TreatmentError):
        log(f"{prefix}: [{exc.code}] {exc.message}")
        return
    log(f"{prefix}: {exc}")
