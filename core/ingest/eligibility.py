from dataclasses import dataclass
import warnings

from core.ingest.dataset_resolver import is_zip_path
from core.ingest.normalization import stringify
from core.ingest.plan import build_ingest_execution_plan
from core.ingest.run_request import IngestRunRequest

REASON_FORCE_ENABLED = "force_enabled"
REASON_SOURCE_PATH_OVERRIDDEN = "source_path_overridden"
REASON_STATUS_NOT_ALLOWED = "status_not_allowed"
REASON_INVALID_STATUS_FLAGS = "invalid_status_flags"
REASON_THEME_NOT_REQUESTED = "theme_not_requested"
REASON_MISSING_SOURCE_PATH = "missing_source_path"
REASON_ZIP_SOURCE_PATH = "zip_source_path"

REASON_MESSAGES = {
    REASON_FORCE_ENABLED: "processamento forcado.",
    REASON_SOURCE_PATH_OVERRIDDEN: "caminho de origem sobrescrito por parametro.",
    REASON_STATUS_NOT_ALLOWED: "status fora dos elegiveis para processamento.",
    REASON_INVALID_STATUS_FLAGS: "status contem flags invalidas.",
    REASON_THEME_NOT_REQUESTED: "theme_folder fora do escopo solicitado.",
    REASON_MISSING_SOURCE_PATH: "caminho de origem ausente ou inexistente.",
    REASON_ZIP_SOURCE_PATH: "Base ignorada porque o caminho informado e um arquivo ZIP.",
}


@dataclass(frozen=True)
class IngestEligibility:
    theme_folder: str
    status: str
    source_path: str
    status_allowed: bool
    theme_requested: bool
    force_enabled: bool
    source_path_overridden: bool
    missing_source_path: bool
    zip_source_path: bool
    invalid_status_flags: tuple[str, ...]
    request_reasons: tuple[str, ...]
    blocking_reasons: tuple[str, ...]

    @property
    def selected_by_request(self):
        return self.status_allowed and self.theme_requested

    @property
    def can_attempt_treatment(self):
        return (
            self.selected_by_request
            and not self.missing_source_path
            and not self.zip_source_path
        )

    @property
    def can_attempt_processing(self):
        warnings.warn(
            "can_attempt_processing esta depreciado; use can_attempt_treatment.",
            DeprecationWarning,
            stacklevel=2,
        )
        return self.can_attempt_treatment

    def request_messages(self):
        return tuple(reason_message(reason) for reason in self.request_reasons)

    def blocking_messages(self):
        return tuple(reason_message(reason) for reason in self.blocking_reasons)


def evaluate_ingest_row(row, run_request):
    theme_folder = stringify(row.get("theme_folder"))
    status = stringify(row.get("status"))
    override_source_path = run_request.source_path_override_for(theme_folder)
    source_path = override_source_path or stringify(row.get("path_shapefile_temp"))

    status_allowed = run_request.is_status_eligible(status, theme_folder)
    theme_requested = run_request.matches_theme_folder(theme_folder)
    force_enabled = run_request.force
    source_path_overridden = bool(override_source_path)
    missing_source_path = not bool(source_path)
    zip_source_path = bool(source_path and is_zip_path(source_path))
    execution_plan = build_ingest_execution_plan(status)
    invalid_flags = execution_plan.invalid_flags

    request_reasons = []
    blocking_reasons = []
    if force_enabled:
        request_reasons.append(REASON_FORCE_ENABLED)
    if source_path_overridden:
        request_reasons.append(REASON_SOURCE_PATH_OVERRIDDEN)
    if invalid_flags:
        blocking_reasons.append(REASON_INVALID_STATUS_FLAGS)
    elif not status_allowed:
        blocking_reasons.append(REASON_STATUS_NOT_ALLOWED)
    if not theme_requested:
        blocking_reasons.append(REASON_THEME_NOT_REQUESTED)
    if missing_source_path:
        blocking_reasons.append(REASON_MISSING_SOURCE_PATH)
    if zip_source_path:
        blocking_reasons.append(REASON_ZIP_SOURCE_PATH)

    return IngestEligibility(
        theme_folder=theme_folder,
        status=status,
        source_path=source_path,
        status_allowed=status_allowed,
        theme_requested=theme_requested,
        force_enabled=force_enabled,
        source_path_overridden=source_path_overridden,
        missing_source_path=missing_source_path,
        zip_source_path=zip_source_path,
        invalid_status_flags=invalid_flags,
        request_reasons=tuple(request_reasons),
        blocking_reasons=tuple(blocking_reasons),
    )


def reason_message(reason):
    return REASON_MESSAGES.get(reason, reason)


__all__ = [
    "IngestEligibility",
    "REASON_FORCE_ENABLED",
    "REASON_INVALID_STATUS_FLAGS",
    "REASON_MESSAGES",
    "REASON_MISSING_SOURCE_PATH",
    "REASON_SOURCE_PATH_OVERRIDDEN",
    "REASON_STATUS_NOT_ALLOWED",
    "REASON_THEME_NOT_REQUESTED",
    "REASON_ZIP_SOURCE_PATH",
    "evaluate_ingest_row",
    "reason_message",
]
