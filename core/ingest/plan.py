from dataclasses import dataclass

from core.ingest.status_flags import parse_ingest_status


@dataclass(frozen=True)
class IngestExecutionPlan:
    status: str
    flags: frozenset[str]
    invalid_flags: tuple[str, ...]
    should_download: bool
    should_treat: bool
    should_publish: bool
    should_schedule: bool
    scheduled_for: object = None

    @property
    def is_valid(self):
        return not self.invalid_flags

    @property
    def is_scheduled_for_treatment(self):
        return self.is_valid and self.should_schedule and bool(self.scheduled_for)


def build_ingest_execution_plan(status):
    ingest_status = parse_ingest_status(status)
    return IngestExecutionPlan(
        status=ingest_status.raw,
        flags=ingest_status.flags,
        invalid_flags=ingest_status.invalid_flags,
        should_download=ingest_status.has_download,
        should_treat=ingest_status.has_treatment,
        should_publish=ingest_status.has_publish,
        should_schedule=ingest_status.has_schedule,
        scheduled_for=ingest_status.scheduled_for,
    )


__all__ = ["IngestExecutionPlan", "build_ingest_execution_plan"]
