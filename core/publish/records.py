from dataclasses import dataclass
from pathlib import Path

import pandas as pd

from core.ingest.normalization import normalize_theme_folder, stringify
from core.ingest.plan import build_ingest_execution_plan
from core.publish.policy import DATA_SUFFIXES
from core.ingest.filters import ThemeFolderFilter
from core.versioning.paths import build_stage_root, normalize_date_folder
from settings import (
    DATA_LAKE_BASE,
    DATA_LAKE_SILVER_STAGE,
    INGEST_SHEET_NAME,
    INGEST_WORKBOOK_PATH,
)


@dataclass(frozen=True)
class PublishRecord:
    sheet_row: int
    record_id: object
    theme_folder: str
    status: str
    silver_dir: str


@dataclass(frozen=True)
class PublishIssue:
    sheet_row: int
    record_id: object
    theme_folder: str
    status: str
    reason: str


def load_publish_records(
    workbook_path=INGEST_WORKBOOK_PATH,
    sheet_name=INGEST_SHEET_NAME,
    theme_folders=None,
    record_filter=None,
):
    dataframe = pd.read_excel(workbook_path, sheet_name=sheet_name)
    record_filter = record_filter or ThemeFolderFilter.from_theme_folders(theme_folders)
    records = []
    issues = []
    publish_candidates = 0

    for idx, row in dataframe.iterrows():
        sheet_row = idx + 2
        record_id = row.get("ID")
        theme_folder = stringify(row.get("theme_folder"))
        status = stringify(row.get("status"))

        execution_plan = build_ingest_execution_plan(status)
        if not execution_plan.should_publish:
            continue

        publish_candidates += 1
        invalid_flags = execution_plan.invalid_flags
        if invalid_flags:
            issues.append(
                PublishIssue(
                    sheet_row=sheet_row,
                    record_id=record_id,
                    theme_folder=theme_folder,
                    status=status,
                    reason=f"Status contem flags invalidas: {', '.join(invalid_flags)}",
                )
            )
            continue

        if not record_filter.matches_theme_folder(theme_folder):
            continue

        try:
            silver_root = build_publish_silver_root(row)
            silver_dir = find_latest_publishable_silver_dir(silver_root)
        except (ValueError, FileNotFoundError) as exc:
            issues.append(
                PublishIssue(
                    sheet_row=sheet_row,
                    record_id=record_id,
                    theme_folder=theme_folder,
                    status=status,
                    reason=str(exc),
                )
            )
            continue

        records.append(
            PublishRecord(
                sheet_row=sheet_row,
                record_id=record_id,
                theme_folder=normalize_theme_folder(theme_folder),
                status=status,
                silver_dir=str(silver_dir),
            )
        )

    summary = {
        "total_records": len(dataframe),
        "publish_candidates": publish_candidates,
        "eligible_records": len(records),
        "issues": len(issues),
        "publish_status": "publish",
    }
    return records, issues, summary


def build_publish_silver_root(row):
    return build_stage_root(
        base_path=DATA_LAKE_BASE,
        stage=DATA_LAKE_SILVER_STAGE,
        access_constraints=_required(row, "access_constraints"),
        category_acronym=_required(row, "category_acronym"),
        theme_folder=normalize_theme_folder(_required(row, "theme_folder")),
        citation=_required(row, "citation"),
        date_folder=normalize_date_folder(_required(row, "date")),
        version=None,
    )


def find_latest_publishable_silver_dir(silver_root):
    silver_root = Path(silver_root)
    versions = sorted(
        (candidate for candidate in silver_root.iterdir() if candidate.is_dir()),
        key=lambda path: path.name,
        reverse=True,
    ) if silver_root.exists() else []

    for version_dir in versions:
        if contains_publishable_data(version_dir):
            return version_dir

    raise FileNotFoundError(f"Nenhuma versao silver publicavel encontrada em: {silver_root}")


def contains_publishable_data(directory):
    return any(
        path.is_file() and path.suffix.lower() in DATA_SUFFIXES
        for path in Path(directory).iterdir()
    )


def _required(row, field):
    value = stringify(row.get(field))
    if not value:
        raise ValueError(f"Campo {field} vazio para publicacao.")
    return value


__all__ = [
    "PublishIssue",
    "PublishRecord",
    "build_publish_silver_root",
    "find_latest_publishable_silver_dir",
    "load_publish_records",
]

