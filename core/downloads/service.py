from pathlib import Path

from core.downloads.config import DownloadRunOptions
from core.tasks.downloads import (
    download_dataset_task,
    emit_dataset_downloaded_event_task,
    extract_download_task,
    resolve_download_version_plan_task,
)
from core.utils import log


def run_data_download(records, run_options=None):
    run_options = run_options or DownloadRunOptions()
    if not records:
        log("Nenhum registro elegivel para download.")
        return []

    return [
        run_single_download(
            record=record,
            dataset_key=record["dataset_key"],
            region=record["region"],
            run_options=run_options,
        )
        for record in records
    ]


def run_single_download(record, dataset_key, region, run_options=None):
    run_options = run_options or DownloadRunOptions()
    version_plan = resolve_download_version_plan_task(record)
    temp_dir = Path(version_plan["temp_dir"])
    archive_output_dir = (
        Path(run_options.output_dir) if run_options.output_dir else temp_dir / "_downloads"
    )
    extract_dir = temp_dir / "raw"

    downloaded = download_dataset_task(
        dataset_key=dataset_key,
        region=region,
        source_root=run_options.source_root,
        output_dir=str(archive_output_dir),
        force=run_options.force,
    )
    extracted = extract_download_task(
        downloaded,
        extract_base=run_options.extract_base,
        extract_dir=str(extract_dir),
    )
    extracted = {
        **extracted,
        "version": version_plan["version"],
        "temp_dir": version_plan["temp_dir"],
        "bronze_dir": version_plan["bronze_dir"],
        "silver_dir": version_plan["silver_dir"],
    }

    if run_options.emit_download_event:
        emit_dataset_downloaded_event_task(extracted)

    return extracted


__all__ = ["run_data_download", "run_single_download"]
