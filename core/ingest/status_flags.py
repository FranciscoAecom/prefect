import re
from dataclasses import dataclass
from datetime import datetime

from core.ingest.normalization import normalize_status, stringify

STATUS_FLAG_DOWNLOAD = "download"
STATUS_FLAG_TREATMENT = "treatment"
STATUS_FLAG_PUBLISH = "publish"
STATUS_FLAG_SCHEDULE = "schedule"
SCHEDULE_STATUS_PATTERN = re.compile(
    r"(?P<prefix>^|[-,;\s])"
    r"schedule"
    r"(?:\s+|[:=]+)"
    r"(?P<scheduled_at>\d{4}-\d{2}-\d{2}[ T]\d{2}:\d{2}(?::\d{2})?)",
    re.IGNORECASE,
)

STATUS_FLAGS = frozenset(
    {
        STATUS_FLAG_DOWNLOAD,
        STATUS_FLAG_TREATMENT,
        STATUS_FLAG_PUBLISH,
        STATUS_FLAG_SCHEDULE,
    }
)


@dataclass(frozen=True)
class IngestStatus:
    raw: str
    flags: frozenset[str]
    invalid_flags: tuple[str, ...]
    scheduled_for: datetime | None = None

    @property
    def is_valid(self):
        return not self.invalid_flags

    def has_flag(self, flag):
        return normalize_status(flag) in self.flags

    @property
    def has_download(self):
        return self.has_flag(STATUS_FLAG_DOWNLOAD)

    @property
    def has_treatment(self):
        return self.has_flag(STATUS_FLAG_TREATMENT)

    @property
    def has_publish(self):
        return self.has_flag(STATUS_FLAG_PUBLISH)

    @property
    def has_schedule(self):
        return self.has_flag(STATUS_FLAG_SCHEDULE)

    @property
    def is_scheduled_for_treatment(self):
        return self.is_valid and self.has_schedule and bool(self.scheduled_for)


def parse_ingest_status(status):
    raw = stringify(status)
    scheduled_for = _parse_status_schedule(raw)
    flags = _parse_status_flags(raw, scheduled_for)
    return IngestStatus(
        raw=raw,
        flags=flags,
        invalid_flags=tuple(sorted(flags - STATUS_FLAGS)),
        scheduled_for=scheduled_for,
    )


def _parse_status_flags(status, scheduled_for):
    text = (
        _status_without_schedule_directive(status)
        if scheduled_for
        else normalize_status(status)
    )
    if not text:
        return frozenset({STATUS_FLAG_SCHEDULE}) if scheduled_for else frozenset()

    parts = [
        part.strip()
        for part in text.replace(",", "-").replace(";", "-").split("-")
        if part.strip()
    ]
    if scheduled_for:
        parts.append(STATUS_FLAG_SCHEDULE)
    return frozenset(parts)


def _parse_status_schedule(status):
    text = stringify(status)
    match = SCHEDULE_STATUS_PATTERN.search(text)
    if not match:
        return None

    scheduled_at = match.group("scheduled_at").replace("T", " ")
    for date_format in ("%Y-%m-%d %H:%M:%S", "%Y-%m-%d %H:%M"):
        try:
            return datetime.strptime(scheduled_at, date_format)
        except ValueError:
            continue
    return None


def _status_without_schedule_directive(status):
    text = normalize_status(status)
    return SCHEDULE_STATUS_PATTERN.sub(lambda match: match.group("prefix"), text).strip(" -,;")


def status_flags_display(flags=STATUS_FLAGS):
    return [stringify(flag) for flag in sorted(flags)]


__all__ = [
    "STATUS_FLAG_DOWNLOAD",
    "STATUS_FLAG_PUBLISH",
    "STATUS_FLAG_SCHEDULE",
    "STATUS_FLAG_TREATMENT",
    "STATUS_FLAGS",
    "IngestStatus",
    "parse_ingest_status",
    "status_flags_display",
]
