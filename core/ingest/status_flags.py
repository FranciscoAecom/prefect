import re
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


def parse_status_flags(status):
    scheduled_at = parse_status_schedule(status)
    text = _status_without_schedule_directive(status) if scheduled_at else normalize_status(status)
    if not text:
        return frozenset({STATUS_FLAG_SCHEDULE}) if scheduled_at else frozenset()

    parts = [
        part.strip()
        for part in text.replace(",", "-").replace(";", "-").split("-")
        if part.strip()
    ]
    if scheduled_at:
        parts.append(STATUS_FLAG_SCHEDULE)
    return frozenset(parts)


def has_status_flag(status, flag):
    return normalize_status(flag) in parse_status_flags(status)


def has_download_flag(status):
    return has_status_flag(status, STATUS_FLAG_DOWNLOAD)


def has_treatment_flag(status):
    return has_status_flag(status, STATUS_FLAG_TREATMENT)


def has_publish_flag(status):
    return has_status_flag(status, STATUS_FLAG_PUBLISH)


def has_schedule_flag(status):
    return has_status_flag(status, STATUS_FLAG_SCHEDULE)


def parse_status_schedule(status):
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


def invalid_status_flags(status):
    return tuple(sorted(parse_status_flags(status) - STATUS_FLAGS))


def find_invalid_status_flags(status):
    return invalid_status_flags(status)


def status_flags_display(flags=STATUS_FLAGS):
    return [stringify(flag) for flag in sorted(flags)]


__all__ = [
    "STATUS_FLAG_DOWNLOAD",
    "STATUS_FLAG_PUBLISH",
    "STATUS_FLAG_SCHEDULE",
    "STATUS_FLAG_TREATMENT",
    "STATUS_FLAGS",
    "has_download_flag",
    "has_publish_flag",
    "has_schedule_flag",
    "has_status_flag",
    "has_treatment_flag",
    "invalid_status_flags",
    "find_invalid_status_flags",
    "parse_status_flags",
    "parse_status_schedule",
    "status_flags_display",
]
