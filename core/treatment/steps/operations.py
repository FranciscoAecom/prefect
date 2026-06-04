from dataclasses import dataclass
from typing import Callable, Literal

from core.validation.normalized_fields import normalized_column_name


OperationKind = Literal["validation", "transform", "normalization", "spatial"]


@dataclass(frozen=True)
class TreatmentOperation:
    name: str
    kind: OperationKind
    handler: Callable
    source_column: str | None = None
    target_column: str | None = None

    def execute(self, gdf, column, **context):
        return self.handler(gdf, column, **context)


def build_treatment_operation(func_name, handler, source_column=None):
    return TreatmentOperation(
        name=func_name,
        kind=infer_treatment_operation_kind(func_name),
        handler=handler,
        source_column=source_column,
        target_column=_target_column(source_column, func_name),
    )


def infer_treatment_operation_kind(func_name):
    name = str(func_name)
    if name.startswith("validate_"):
        return "validation"
    if "transform" in name:
        return "transform"
    if "normaliz" in name:
        return "normalization"
    if "spatial" in name or "geometry" in name or "bbox" in name:
        return "spatial"
    return "transform"


def _target_column(source_column, func_name):
    if not source_column or infer_treatment_operation_kind(func_name) == "validation":
        return None
    return normalized_column_name(source_column)


infer_operation_kind = infer_treatment_operation_kind


__all__ = [
    "OperationKind",
    "TreatmentOperation",
    "build_treatment_operation",
    "infer_treatment_operation_kind",
    "infer_operation_kind",
]
