from dataclasses import dataclass

import pandas as pd

from core.downloads.catalog import (
    resolve_download_target_for_theme_folder,
    resolve_region_from_theme_folder,
)
from core.ingest.normalization import normalize_theme_folder, stringify
from core.ingest.plan import build_ingest_execution_plan
from core.queue.filters import QueueFilter
from settings import INGEST_DOWNLOAD_STATUS, INGEST_SHEET_NAME, INGEST_WORKBOOK_PATH


@dataclass(frozen=True)
class DownloadQueueRecord:
    sheet_row: int
    record_id: object
    theme: str
    theme_folder: str
    status: str
    dataset_key: str
    region: str | None
    connector: str
    access_constraints: str = ""
    category_acronym: str = ""
    citation: str = ""
    date: str = ""


@dataclass(frozen=True)
class DownloadQueueIssue:
    sheet_row: int
    record_id: object
    theme_folder: str
    status: str
    reason: str


def load_download_queue(
    workbook_path=INGEST_WORKBOOK_PATH,
    sheet_name=INGEST_SHEET_NAME,
    download_status=INGEST_DOWNLOAD_STATUS,
    theme_folders=None,
    queue_filter=None,
):
    dataframe = pd.read_excel(workbook_path, sheet_name=sheet_name)
    queue_filter = queue_filter or QueueFilter.from_theme_folders(theme_folders)

    eligible_records = []
    issues = []
    download_candidates = 0

    for idx, row in dataframe.iterrows():
        sheet_row = idx + 2
        record_id = row.get("ID")
        theme = stringify(row.get("theme"))
        theme_folder = stringify(row.get("theme_folder"))
        status = stringify(row.get("status"))
        versioning_metadata = _extract_versioning_metadata(row)

        execution_plan = build_ingest_execution_plan(status)
        if not execution_plan.should_download:
            continue

        download_candidates += 1

        invalid_flags = execution_plan.invalid_flags
        if invalid_flags:
            issues.append(
                DownloadQueueIssue(
                    sheet_row=sheet_row,
                    record_id=record_id,
                    theme_folder=theme_folder,
                    status=status,
                    reason=f"Status contem flags invalidas: {', '.join(invalid_flags)}",
                )
            )
            continue

        if not queue_filter.matches_theme_folder(theme_folder):
            continue

        target = resolve_download_target_for_theme_folder(theme_folder)
        if target is None:
            issues.append(
                DownloadQueueIssue(
                    sheet_row=sheet_row,
                    record_id=record_id,
                    theme_folder=theme_folder,
                    status=status,
                    reason=(
                        "Base marcada para Download, mas nao existe conector/script "
                        "de download registrado para este theme_folder."
                    ),
                )
            )
            continue

        try:
            region = resolve_region_from_theme_folder(target, theme_folder)
        except ValueError as exc:
            issues.append(
                DownloadQueueIssue(
                    sheet_row=sheet_row,
                    record_id=record_id,
                    theme_folder=theme_folder,
                    status=status,
                    reason=str(exc),
                )
            )
            continue

        eligible_records.append(
            DownloadQueueRecord(
                sheet_row=sheet_row,
                record_id=record_id,
                theme=theme,
                theme_folder=normalize_theme_folder(theme_folder),
                status=status,
                dataset_key=target.key,
                region=region,
                connector=target.connector,
                **versioning_metadata,
            )
        )

    summary = {
        "total_records": len(dataframe),
        "download_candidates": download_candidates,
        "eligible_records": len(eligible_records),
        "issues": len(issues),
        "download_status": download_status,
    }
    return eligible_records, issues, summary


def _extract_versioning_metadata(row):
    return {
        "access_constraints": stringify(row.get("access_constraints")),
        "category_acronym": stringify(row.get("category_acronym")),
        "citation": stringify(row.get("citation")),
        "date": stringify(row.get("date")),
    }


__all__ = ["DownloadQueueIssue", "DownloadQueueRecord", "load_download_queue"]
