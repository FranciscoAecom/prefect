from dataclasses import dataclass

from core.ingest.normalization import normalize_theme_folder, stringify


@dataclass(frozen=True)
class QueueFilter:
    theme_folders: frozenset[str] = frozenset()

    @classmethod
    def from_theme_folders(cls, theme_folders=None):
        return cls(theme_folders=_normalize_theme_folders(theme_folders))

    def matches_theme_folder(self, theme_folder):
        if not self.theme_folders:
            return True
        return normalize_theme_folder(theme_folder) in self.theme_folders


def _normalize_theme_folders(theme_folders):
    if theme_folders is None:
        return frozenset()
    if isinstance(theme_folders, dict):
        if theme_folders.get("__prefect_kind") == "json":
            theme_folders = theme_folders.get("value")
        else:
            theme_folders = theme_folders.values()
    if isinstance(theme_folders, str):
        theme_folders = _parse_theme_folder_string(theme_folders)
    return frozenset(
        normalized
        for normalized in (normalize_theme_folder(value) for value in theme_folders)
        if normalized
    )


def _parse_theme_folder_string(theme_folders):
    import json

    text = stringify(theme_folders)
    if not text:
        return []
    try:
        parsed = json.loads(text)
    except json.JSONDecodeError:
        return [text]
    if isinstance(parsed, str):
        return [parsed]
    return parsed


__all__ = ["QueueFilter"]
