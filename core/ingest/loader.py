import pandas as pd

from core.ingest.dataset_resolver import (
    is_zip_path,
    resolve_input_dataset_paths_cached,
)
from core.ingest.models import IngestIssue, IngestRecord
from core.ingest.normalization import normalize_status, normalize_theme_folder, stringify
from core.queue.filters import QueueFilter
from core.rules.engine import (
    RuleProfileResolutionError,
    expected_rule_profile_name,
    find_rule_profile_by_theme_folder,
    get_rule_profile_project_name,
)
from projects.configs import resolve_project_name
from settings import (
    INGEST_READY_STATUS,
    INGEST_SHEET_NAME,
    INGEST_WORKBOOK_PATH,
)


def load_processing_queue(
    workbook_path=INGEST_WORKBOOK_PATH,
    sheet_name=INGEST_SHEET_NAME,
    ready_status=INGEST_READY_STATUS,
    theme_folders=None,
    queue_filter=None,
    source_path_overrides=None,
):
    dataframe = pd.read_excel(workbook_path, sheet_name=sheet_name)
    ready_status_normalized = normalize_status(ready_status)
    queue_filter = queue_filter or QueueFilter.from_theme_folders(theme_folders)
    source_path_overrides = _normalize_source_path_overrides(source_path_overrides)

    eligible_records = []
    issues = []
    ready_candidates = 0

    for idx, row in dataframe.iterrows():
        sheet_row = idx + 2
        record_id = row.get("ID")
        theme = stringify(row.get("theme"))
        theme_folder = stringify(row.get("theme_folder"))
        status = stringify(row.get("status"))
        override_source_path = source_path_overrides.get(normalize_theme_folder(theme_folder))
        source_path = override_source_path or stringify(row.get("path_shapefile_temp"))

        if normalize_status(status) != ready_status_normalized and not override_source_path:
            continue

        ready_candidates += 1

        if not queue_filter.matches_theme_folder(theme_folder):
            continue

        if is_zip_path(source_path):
            issues.append(
                IngestIssue(
                    sheet_row=sheet_row,
                    record_id=record_id,
                    theme_folder=theme_folder,
                    status=status,
                    source_path=source_path,
                    reason="Base ignorada porque o caminho informado e um arquivo ZIP.",
                )
            )
            continue

        expected_rule_profile = expected_rule_profile_name(theme_folder)
        try:
            rule_profile = find_rule_profile_by_theme_folder(theme_folder)
        except RuleProfileResolutionError as exc:
            issues.append(
                IngestIssue(
                    sheet_row=sheet_row,
                    record_id=record_id,
                    theme_folder=theme_folder,
                    status=status,
                    source_path=source_path,
                    reason=str(exc),
                )
            )
            continue

        if not rule_profile:
            issues.append(
                IngestIssue(
                    sheet_row=sheet_row,
                    record_id=record_id,
                    theme_folder=theme_folder,
                    status=status,
                    source_path=source_path,
                    reason=(
                        "Nenhum arquivo de regra correspondente foi encontrado em rules/. "
                        f"Perfil esperado: rules/{expected_rule_profile}.json."
                    ),
                )
            )
            continue

        resolved_project_name = resolve_project_name(theme_folder)
        rule_project_name = get_rule_profile_project_name(rule_profile)
        if rule_project_name and rule_project_name != resolved_project_name:
            issues.append(
                IngestIssue(
                    sheet_row=sheet_row,
                    record_id=record_id,
                    theme_folder=theme_folder,
                    status=status,
                    source_path=source_path,
                    reason=(
                        "Perfil de regras inconsistente com o projeto resolvido: "
                        f"theme_folder={theme_folder} -> projeto {resolved_project_name}, "
                        f"mas o perfil {rule_profile} declara project_name={rule_project_name}."
                    ),
                )
            )
            continue

        try:
            input_paths = resolve_input_dataset_paths_cached(source_path)
        except (FileNotFoundError, ValueError, PermissionError, OSError) as exc:
            issues.append(
                IngestIssue(
                    sheet_row=sheet_row,
                    record_id=record_id,
                    theme_folder=theme_folder,
                    status=status,
                    source_path=source_path,
                    reason=str(exc),
                )
            )
            continue

        for input_path in input_paths:
            eligible_records.append(
                IngestRecord(
                    sheet_row=sheet_row,
                    record_id=record_id,
                    theme=theme,
                    theme_folder=theme_folder,
                    status=status,
                    source_path=source_path,
                    input_path=input_path,
                    rule_profile=rule_profile,
                )
            )

    summary = {
        "total_records": len(dataframe),
        "ready_candidates": ready_candidates,
        "eligible_records": len(eligible_records),
        "issues": len(issues),
    }

    return eligible_records, issues, summary


def _normalize_source_path_overrides(source_path_overrides):
    if not source_path_overrides:
        return {}
    return {
        normalize_theme_folder(theme_folder): stringify(source_path)
        for theme_folder, source_path in dict(source_path_overrides).items()
        if normalize_theme_folder(theme_folder) and stringify(source_path)
    }


__all__ = ["load_processing_queue"]
