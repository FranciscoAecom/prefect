import re

from core.ingest.filters import ThemeFolderFilter


def normalize_theme_folders_for_name(theme_folders):
    return sorted(ThemeFolderFilter.from_theme_folders(theme_folders).theme_folders)


def safe_flow_name_part(value, fallback="item"):
    text = str(value or "").replace("\\", "/").rstrip("/").split("/")[-1]
    text = re.sub(r"[^A-Za-z0-9_=-]+", "_", text).strip("_")
    return text or fallback


def flow_run_name():
    from prefect.runtime import flow_run

    parameters = flow_run.parameters or {}
    theme_folders = normalize_theme_folders_for_name(parameters.get("theme_folders"))
    if len(theme_folders) == 1:
        return theme_folders[0]
    if theme_folders:
        return f"{len(theme_folders)} bases"
    return "Data Treatment"


def record_task_run_name(parameters):
    record = parameters["record"]
    return str(getattr(record, "theme_folder", "") or "sem_theme_folder")


def scheduled_flow_run_name(parameters):
    theme_folders = normalize_theme_folders_for_name(
        (parameters or {}).get("theme_folders")
    )
    if len(theme_folders) == 1:
        return theme_folders[0]
    if theme_folders:
        return f"{len(theme_folders)} bases"
    return "Data Treatment"


def publish_flow_run_name_for_parameters(parameters):
    parameters = parameters or {}
    theme_folders = normalize_theme_folders_for_name(parameters.get("theme_folders"))
    if len(theme_folders) == 1:
        return f"publish_{theme_folders[0]}"
    if theme_folders:
        return f"publish_{len(theme_folders)}_bases"
    if parameters.get("folder"):
        return f"publish_{safe_flow_name_part(parameters['folder'], 'folder')}"
    return "publish_ingest"


def publish_flow_run_name():
    from prefect.runtime import flow_run

    return publish_flow_run_name_for_parameters(flow_run.parameters or {})


__all__ = [
    "flow_run_name",
    "normalize_theme_folders_for_name",
    "publish_flow_run_name",
    "publish_flow_run_name_for_parameters",
    "record_task_run_name",
    "safe_flow_name_part",
    "scheduled_flow_run_name",
]
