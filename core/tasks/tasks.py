from core.tasks.downloads import (
    download_dataset_task,
    emit_dataset_downloaded_event_task,
    extract_download_task,
    load_download_queue_task,
    resolve_download_version_plan_task,
)
from core.tasks.treatment import (
    prepare_treatment_run_task,
    run_treatment_record_task,
)
from core.tasks.publish import discover_publish_items_task, publish_item_task


PREFECT_TASKS = {
    "prepare_treatment_run": prepare_treatment_run_task,
    "run_treatment_record": run_treatment_record_task,
    "download_dataset": download_dataset_task,
    "extract_download": extract_download_task,
    "emit_dataset_downloaded_event": emit_dataset_downloaded_event_task,
    "load_download_queue": load_download_queue_task,
    "resolve_download_version_plan": resolve_download_version_plan_task,
    "discover_publish_items": discover_publish_items_task,
    "publish_item": publish_item_task,
}


__all__ = [
    "PREFECT_TASKS",
    "discover_publish_items_task",
    "download_dataset_task",
    "emit_dataset_downloaded_event_task",
    "extract_download_task",
    "load_download_queue_task",
    "prepare_treatment_run_task",
    "publish_item_task",
    "resolve_download_version_plan_task",
    "run_treatment_record_task",
]
