from core.ingest.dataset_resolver import (
    is_zip_path,
    resolve_input_dataset_paths_cached,
)
from core.ingest.models import IngestIssue, IngestRecord
from core.ingest.normalization import normalize_status, normalize_theme_folder, stringify
from core.ingest.repository import build_ingest_repository
from core.ingest.run_request import IngestRunRequest
from core.queue.filters import QueueFilter
from core.rules.engine import (
    RuleProfileResolutionError,
    resolve_rule_profile_for_theme,
)
from core.versioning import resolve_dataset_version_plan
from settings import (
    INGEST_PROCESSING_STATUSES,
    INGEST_READY_STATUS,
    INGEST_SHEET_NAME,
    INGEST_WORKBOOK_PATH,
)


def load_processing_queue(
    workbook_path=INGEST_WORKBOOK_PATH,
    sheet_name=INGEST_SHEET_NAME,
    ready_status=INGEST_PROCESSING_STATUSES,
    theme_folders=None,
    queue_filter=None,
    source_path_overrides=None,
    repository=None,
    run_request=None,
    force=False,
):
    run_request = run_request or IngestRunRequest.from_legacy(
        theme_folders=theme_folders,
        ready_status=ready_status,
        queue_filter=queue_filter,
        source_path_overrides=source_path_overrides,
        force=force,
    )
    ingest_repository = build_ingest_repository(
        workbook_path=workbook_path,
        sheet_name=sheet_name,
        repository=repository,
    )

    eligible_records = []
    issues = []
    ready_candidates = 0

    total_records = 0
    for catalog_row in ingest_repository.iter_rows():
        total_records += 1
        row = catalog_row.data
        sheet_row = catalog_row.sheet_row
        record_id = row.get("ID")
        theme = stringify(row.get("theme"))
        theme_folder = stringify(row.get("theme_folder"))
        status = stringify(row.get("status"))
        versioning_metadata = _extract_versioning_metadata(row)
        xml_metadata = _extract_xml_metadata(row)
        override_source_path = run_request.source_path_override_for(theme_folder)
        source_path = override_source_path or stringify(row.get("path_shapefile_temp"))

        if not run_request.is_status_eligible(status, theme_folder):
            continue

        ready_candidates += 1

        if not run_request.matches_theme_folder(theme_folder):
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

        try:
            rule_resolution = resolve_rule_profile_for_theme(theme_folder)
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

        if not rule_resolution.found:
            issues.append(
                IngestIssue(
                    sheet_row=sheet_row,
                    record_id=record_id,
                    theme_folder=theme_folder,
                    status=status,
                    source_path=source_path,
                    reason=(
                        "Nenhum arquivo de regra correspondente foi encontrado em rules/. "
                        f"Perfil esperado: rules/{rule_resolution.expected_profile_name}."
                    ),
                )
            )
            continue

        if rule_resolution.missing_components:
            issues.append(
                IngestIssue(
                    sheet_row=sheet_row,
                    record_id=record_id,
                    theme_folder=theme_folder,
                    status=status,
                    source_path=source_path,
                    reason=(
                        "Perfil de regras incompleto: "
                        f"{rule_resolution.profile_name} sem "
                        + ", ".join(rule_resolution.missing_components)
                        + "."
                    ),
                )
            )
            continue

        if not rule_resolution.project_consistent:
            issues.append(
                IngestIssue(
                    sheet_row=sheet_row,
                    record_id=record_id,
                    theme_folder=theme_folder,
                    status=status,
                    source_path=source_path,
                    reason=(
                        "Perfil de regras inconsistente com o projeto resolvido: "
                        f"theme_folder={theme_folder} -> projeto {rule_resolution.project_name}, "
                        f"mas o perfil {rule_resolution.profile_name} declara "
                        f"project_name={rule_resolution.profile_project_name}."
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
            versioned_dirs = _resolve_versioned_dirs(
                {
                    "status": status,
                    "theme_folder": theme_folder,
                    **versioning_metadata,
                }
            )
            eligible_records.append(
                IngestRecord(
                    sheet_row=sheet_row,
                    record_id=record_id,
                    theme=theme,
                    theme_folder=theme_folder,
                    status=status,
                    source_path=source_path,
                    input_path=input_path,
                    rule_profile=rule_resolution.profile_name,
                    **versioning_metadata,
                    **xml_metadata,
                    output_dir=versioned_dirs["output_dir"],
                    bronze_dir=versioned_dirs["bronze_dir"],
                    temp_dir=versioned_dirs["temp_dir"],
                )
            )

    summary = {
        "total_records": total_records,
        "ready_candidates": ready_candidates,
        "eligible_records": len(eligible_records),
        "issues": len(issues),
        "processing_statuses": run_request.processing_statuses_display(),
        "force": run_request.force,
    }

    return eligible_records, issues, summary


def _extract_versioning_metadata(row):
    return {
        "access_constraints": stringify(row.get("access_constraints")),
        "category_acronym": stringify(row.get("category_acronym")),
        "citation": stringify(row.get("citation")),
        "date": stringify(row.get("date")),
    }


def _extract_xml_metadata(row):
    fields = (
        "id_geonetwork",
        "abstract",
        "use_constraints",
        "data_classification",
        "data_activity_classification",
        "topic_category_code",
        "spatial_representation_type_code",
        "maintenance_frequency_code",
        "maintenance_frequency_aecom",
        "responsible_party",
        "beginposition",
        "endposition",
        "source",
        "reference_system",
        "data_dictionary",
        "metadata",
        "methodologie",
        "others",
        "date_stamp",
        "project",
        "characterstring",
    )
    return {field: stringify(row.get(field)) for field in fields}


def _resolve_versioned_dirs(record):
    if not all(
        stringify(record.get(field))
        for field in (
            "status",
            "access_constraints",
            "category_acronym",
            "theme_folder",
            "citation",
            "date",
        )
    ):
        return {"output_dir": "", "bronze_dir": "", "temp_dir": ""}
    plan = resolve_dataset_version_plan(record)
    return {
        "output_dir": str(plan.silver_dir),
        "bronze_dir": str(plan.bronze_dir),
        "temp_dir": str(plan.temp_dir),
    }

__all__ = ["load_processing_queue"]
