from core.ingest.normalization import normalize_status, stringify

STATUS_FLAG_DOWNLOAD = "download"
STATUS_FLAG_TREATMENT = "treatment"
STATUS_FLAG_PUBLISH = "publish"

STATUS_FLAGS = frozenset(
    {
        STATUS_FLAG_DOWNLOAD,
        STATUS_FLAG_TREATMENT,
        STATUS_FLAG_PUBLISH,
    }
)


def parse_status_flags(status):
    text = normalize_status(status)
    if not text:
        return frozenset()

    parts = [
        part.strip()
        for part in text.replace(",", "-").replace(";", "-").split("-")
        if part.strip()
    ]
    return frozenset(parts)


def has_status_flag(status, flag):
    return normalize_status(flag) in parse_status_flags(status)


def has_download_flag(status):
    return has_status_flag(status, STATUS_FLAG_DOWNLOAD)


def has_treatment_flag(status):
    return has_status_flag(status, STATUS_FLAG_TREATMENT)


def has_publish_flag(status):
    return has_status_flag(status, STATUS_FLAG_PUBLISH)


def invalid_status_flags(status):
    return tuple(sorted(parse_status_flags(status) - STATUS_FLAGS))


def find_invalid_status_flags(status):
    return invalid_status_flags(status)


def status_flags_display(flags=STATUS_FLAGS):
    return [stringify(flag) for flag in sorted(flags)]


__all__ = [
    "STATUS_FLAG_DOWNLOAD",
    "STATUS_FLAG_PUBLISH",
    "STATUS_FLAG_TREATMENT",
    "STATUS_FLAGS",
    "has_download_flag",
    "has_publish_flag",
    "has_status_flag",
    "has_treatment_flag",
    "invalid_status_flags",
    "find_invalid_status_flags",
    "parse_status_flags",
    "status_flags_display",
]
