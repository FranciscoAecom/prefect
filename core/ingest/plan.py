from dataclasses import dataclass

from core.ingest.status_flags import (
    has_download_flag,
    has_publish_flag,
    has_treatment_flag,
    invalid_status_flags,
    parse_status_flags,
)


@dataclass(frozen=True)
class IngestExecutionPlan:
    status: str
    flags: frozenset[str]
    invalid_flags: tuple[str, ...]
    should_download: bool
    should_treat: bool
    should_publish: bool

    @property
    def is_valid(self):
        return not self.invalid_flags


def build_ingest_execution_plan(status):
    flags = parse_status_flags(status)
    return IngestExecutionPlan(
        status=str(status or ""),
        flags=flags,
        invalid_flags=invalid_status_flags(status),
        should_download=has_download_flag(status),
        should_treat=has_treatment_flag(status),
        should_publish=has_publish_flag(status),
    )


__all__ = ["IngestExecutionPlan", "build_ingest_execution_plan"]
