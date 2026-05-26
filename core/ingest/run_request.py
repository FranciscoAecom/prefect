from dataclasses import dataclass, field

from core.ingest.normalization import normalize_status, normalize_theme_folder, stringify
from core.queue.filters import QueueFilter
from settings import INGEST_PROCESSING_STATUSES, INGEST_READY_STATUS


@dataclass(frozen=True)
class IngestRunRequest:
    theme_folders: tuple[str, ...] = ()
    ready_statuses: tuple[str, ...] = INGEST_PROCESSING_STATUSES
    source_path_overrides: dict[str, str] = field(default_factory=dict)
    force: bool = False

    @classmethod
    def from_legacy(
        cls,
        *,
        theme_folders=None,
        ready_status=None,
        queue_filter=None,
        source_path_overrides=None,
        force=False,
    ):
        if isinstance(theme_folders, cls):
            return theme_folders
        effective_filter = queue_filter or QueueFilter.from_theme_folders(theme_folders)
        return cls(
            theme_folders=tuple(sorted(effective_filter.theme_folders)),
            ready_statuses=normalize_ready_statuses_for_request(ready_status),
            source_path_overrides=normalize_source_path_overrides(source_path_overrides),
            force=bool(force),
        )

    @property
    def queue_filter(self):
        return QueueFilter(theme_folders=frozenset(self.theme_folders))

    def matches_theme_folder(self, theme_folder):
        return self.queue_filter.matches_theme_folder(theme_folder)

    def source_path_override_for(self, theme_folder):
        return self.source_path_overrides.get(normalize_theme_folder(theme_folder), "")

    def is_status_eligible(self, status, theme_folder=None):
        if self.force:
            return True
        if theme_folder and self.source_path_override_for(theme_folder):
            return True
        return normalize_status(status) in {
            normalize_status(value)
            for value in self.ready_statuses
            if normalize_status(value)
        }

    def processing_statuses_display(self):
        return [stringify(status) for status in self.ready_statuses if stringify(status)]

    def to_diagnostic_context(self):
        return {
            "theme_folders": list(self.theme_folders),
            "ready_statuses": self.processing_statuses_display(),
            "force": self.force,
            "source_path_overrides": dict(self.source_path_overrides),
        }


def normalize_ready_statuses_for_request(ready_status):
    if isinstance(ready_status, str):
        statuses = [ready_status]
    else:
        statuses = list(ready_status or [INGEST_READY_STATUS])
    return tuple(stringify(status) for status in statuses if stringify(status))


def normalize_source_path_overrides(source_path_overrides):
    if not source_path_overrides:
        return {}
    return {
        normalize_theme_folder(theme_folder): stringify(source_path)
        for theme_folder, source_path in dict(source_path_overrides).items()
        if normalize_theme_folder(theme_folder) and stringify(source_path)
    }


__all__ = [
    "IngestRunRequest",
    "normalize_ready_statuses_for_request",
    "normalize_source_path_overrides",
]
