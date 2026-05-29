from core.ingest.dataset_resolver import resolve_input_dataset_paths_cached
from core.ingest.eligibility import evaluate_ingest_row
from core.ingest.issues import (
    incomplete_rule_profile_issue,
    inconsistent_rule_profile_issue,
    input_dataset_resolution_error_issue,
    missing_rule_profile_issue,
    missing_source_path_issue,
    rule_profile_resolution_error_issue,
    zip_source_path_issue,
)
from core.ingest.models import IngestRecord
from core.ingest.normalization import stringify
from core.ingest.repository import build_ingest_repository
from core.ingest.run_request import IngestRunRequest
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
    run_request = _build_run_request(
        run_request=run_request,
        theme_folders=theme_folders,
        ready_status=ready_status,
        queue_filter=queue_filter,
        source_path_overrides=source_path_overrides,
        force=force,
    )
    ingest_repository = _build_repository(workbook_path, sheet_name, repository)
    eligible_records = []
    issues = []
    ready_candidates = 0
    total_records = 0

    for catalog_row in ingest_repository.iter_rows():
        total_records += 1
        queue_entry = _build_queue_entry(catalog_row, run_request)

        if not queue_entry["eligibility"].status_allowed:
            continue

        ready_candidates += 1

        if not queue_entry["eligibility"].theme_requested:
            continue

        input_issue = _resolve_input_issue(queue_entry)
        if input_issue:
            issues.append(input_issue)
            continue

        rule_resolution, rule_issue = _resolve_rule_profile(queue_entry)
        if rule_issue:
            issues.append(rule_issue)
            continue

        input_paths, dataset_issue = _resolve_input_paths(queue_entry)
        if dataset_issue:
            issues.append(dataset_issue)
            continue

        eligible_records.extend(
            _build_records_for_input_paths(queue_entry, rule_resolution, input_paths)
        )

    summary = _build_summary(total_records, ready_candidates, eligible_records, issues, run_request)
    return eligible_records, issues, summary


def _build_run_request(
    run_request,
    theme_folders,
    ready_status,
    queue_filter,
    source_path_overrides,
    force,
):
    return run_request or IngestRunRequest.from_legacy(
        theme_folders=theme_folders,
        ready_status=ready_status,
        queue_filter=queue_filter,
        source_path_overrides=source_path_overrides,
        force=force,
    )


def _build_repository(workbook_path, sheet_name, repository):
    return build_ingest_repository(
        workbook_path=workbook_path,
        sheet_name=sheet_name,
        repository=repository,
    )


def _build_queue_entry(catalog_row, run_request):
    row = catalog_row.data
    theme_folder = stringify(row.get("theme_folder"))
    status = stringify(row.get("status"))
    eligibility = evaluate_ingest_row(row, run_request)
    source_path = eligibility.source_path
    return {
        "sheet_row": catalog_row.sheet_row,
        "record_id": row.get("ID"),
        "theme": stringify(row.get("theme")),
        "theme_folder": theme_folder,
        "status": status,
        "source_path": source_path,
        "versioning_metadata": _extract_versioning_metadata(row),
        "xml_metadata": _extract_xml_metadata(row),
        "eligibility": eligibility,
        "issue_context": {
            "sheet_row": catalog_row.sheet_row,
            "record_id": row.get("ID"),
            "theme_folder": theme_folder,
            "status": status,
            "source_path": source_path,
        },
    }


def _resolve_input_issue(queue_entry):
    eligibility = queue_entry["eligibility"]
    issue_context = queue_entry["issue_context"]

    if eligibility.missing_source_path:
        return missing_source_path_issue(issue_context)
    if eligibility.zip_source_path:
        return zip_source_path_issue(issue_context)
    return None


def _resolve_rule_profile(queue_entry):
    issue_context = queue_entry["issue_context"]
    try:
        rule_resolution = resolve_rule_profile_for_theme(queue_entry["theme_folder"])
    except RuleProfileResolutionError as exc:
        return None, rule_profile_resolution_error_issue(issue_context, exc)

    if not rule_resolution.found:
        return None, missing_rule_profile_issue(issue_context, rule_resolution)
    if rule_resolution.missing_components:
        return None, incomplete_rule_profile_issue(issue_context, rule_resolution)
    if not rule_resolution.project_consistent:
        return None, inconsistent_rule_profile_issue(issue_context, rule_resolution)

    return rule_resolution, None


def _resolve_input_paths(queue_entry):
    try:
        return resolve_input_dataset_paths_cached(queue_entry["source_path"]), None
    except (FileNotFoundError, ValueError, PermissionError, OSError) as exc:
        return None, input_dataset_resolution_error_issue(
            queue_entry["issue_context"],
            exc,
        )


def _build_records_for_input_paths(queue_entry, rule_resolution, input_paths):
    records = []
    for input_path in input_paths:
        versioned_dirs = _resolve_versioned_dirs(
            {
                "status": queue_entry["status"],
                "theme_folder": queue_entry["theme_folder"],
                **queue_entry["versioning_metadata"],
            }
        )
        records.append(
            IngestRecord(
                sheet_row=queue_entry["sheet_row"],
                record_id=queue_entry["record_id"],
                theme=queue_entry["theme"],
                theme_folder=queue_entry["theme_folder"],
                status=queue_entry["status"],
                source_path=queue_entry["source_path"],
                input_path=input_path,
                rule_profile=rule_resolution.profile_name,
                **queue_entry["versioning_metadata"],
                **queue_entry["xml_metadata"],
                output_dir=versioned_dirs["output_dir"],
                bronze_dir=versioned_dirs["bronze_dir"],
                temp_dir=versioned_dirs["temp_dir"],
            )
        )
    return records


def _build_summary(total_records, ready_candidates, eligible_records, issues, run_request):
    return {
        "total_records": total_records,
        "ready_candidates": ready_candidates,
        "eligible_records": len(eligible_records),
        "issues": len(issues),
        "processing_statuses": run_request.processing_statuses_display(),
        "force": run_request.force,
    }


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
