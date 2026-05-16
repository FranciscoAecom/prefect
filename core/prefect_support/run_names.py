from core.queue.filters import QueueFilter


def normalize_theme_folders_for_name(theme_folders):
    return sorted(QueueFilter.from_theme_folders(theme_folders).theme_folders)


def flow_run_name():
    from prefect.runtime import flow_run

    parameters = flow_run.parameters or {}
    theme_folders = normalize_theme_folders_for_name(parameters.get("theme_folders"))
    if len(theme_folders) == 1:
        return theme_folders[0]
    if theme_folders:
        return f"{len(theme_folders)} bases"
    return "Data Pipeline"


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
    return "Data Pipeline"


__all__ = [
    "flow_run_name",
    "normalize_theme_folders_for_name",
    "record_task_run_name",
    "scheduled_flow_run_name",
]
