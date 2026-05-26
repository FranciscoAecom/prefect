from pathlib import Path

from core.ingest.normalization import normalize_status, normalize_theme_folder, stringify
from core.ingest.repository import build_ingest_repository
from core.ingest.run_request import IngestRunRequest
from core.rules.engine import resolve_rule_profile_for_theme
from settings import (
    INGEST_PROCESSING_STATUSES,
    INGEST_SHEET_NAME,
    INGEST_WORKBOOK_PATH,
)


def diagnose_ingest_theme(
    theme_folder,
    workbook_path=INGEST_WORKBOOK_PATH,
    sheet_name=INGEST_SHEET_NAME,
    ready_status=INGEST_PROCESSING_STATUSES,
    repository=None,
    run_request=None,
    force=False,
):
    run_request = run_request or IngestRunRequest.from_legacy(
        theme_folders=[theme_folder],
        ready_status=ready_status,
        source_path_overrides=None,
        force=force,
    )
    target_theme = normalize_theme_folder(theme_folder)
    ingest_repository = build_ingest_repository(
        workbook_path=workbook_path,
        sheet_name=sheet_name,
        repository=repository,
    )
    matches = []

    for catalog_row in ingest_repository.iter_rows():
        row = catalog_row.data
        row_theme_folder = stringify(row.get("theme_folder"))
        if normalize_theme_folder(row_theme_folder) != target_theme:
            continue

        status = stringify(row.get("status"))
        override_source_path = run_request.source_path_override_for(row_theme_folder)
        source_path = override_source_path or stringify(row.get("path_shapefile_temp"))
        rule_resolution = resolve_rule_profile_for_theme(
            row_theme_folder,
            raise_on_error=False,
        )

        source_exists = bool(source_path and Path(source_path).exists())
        matches.append(
            {
                "sheet_row": catalog_row.sheet_row,
                "record_id": row.get("ID"),
                "theme": stringify(row.get("theme")),
                "theme_folder": row_theme_folder,
                "status": status,
                "status_eligible": run_request.is_status_eligible(status, row_theme_folder),
                "force": run_request.force,
                "source_path_overridden": bool(override_source_path),
                "source_path": source_path,
                "source_exists": source_exists,
                "project_name": rule_resolution.project_name,
                "expected_rule_profile": rule_resolution.expected_profile_name,
                "found_rule_profile": rule_resolution.profile_name,
                "profile_error": rule_resolution.error,
                "missing_rule_components": rule_resolution.missing_components,
                "profile_project_name": rule_resolution.profile_project_name,
                "profile_project_consistent": rule_resolution.project_consistent,
            }
        )

    return {
        "theme_folder": theme_folder,
        "normalized_theme_folder": target_theme,
        "workbook_path": str(workbook_path),
        "sheet_name": sheet_name,
        "ready_statuses": run_request.processing_statuses_display(),
        "run_request": run_request.to_diagnostic_context(),
        "matches": matches,
    }


def format_ingest_theme_diagnostic(diagnostic):
    lines = [
        f"Diagnostico theme_folder={diagnostic['theme_folder']}",
        f"  Planilha: {diagnostic['workbook_path']}",
        f"  Aba: {diagnostic['sheet_name']}",
        "  Status elegiveis: " + ", ".join(str(s) for s in diagnostic["ready_statuses"]),
    ]
    matches = diagnostic["matches"]
    if not matches:
        lines.append("  Nenhuma linha encontrada para esse theme_folder.")
        return lines

    lines.append(f"  Linhas encontradas: {len(matches)}")
    for match in matches:
        lines.extend(format_ingest_theme_match(match))
    return lines


def format_ingest_theme_match(match):
    status_marker = "sim" if match["status_eligible"] else "nao"
    source_marker = "sim" if match["source_exists"] else "nao"
    found_profile = match["found_rule_profile"] or "<nao encontrado>"
    lines = [
        f"  Linha {match['sheet_row']} | ID={match['record_id']}",
        f"    theme: {match['theme']}",
        f"    theme_folder: {match['theme_folder']}",
        f"    status: {match['status']} | elegivel: {status_marker}",
        f"    source_path existe: {source_marker} | {match['source_path'] or '<vazio>'}",
        f"    projeto resolvido: {match['project_name']}",
        f"    perfil esperado: {match['expected_rule_profile']}",
        f"    perfil encontrado: {found_profile}",
    ]
    if match["profile_error"]:
        lines.append(f"    erro perfil: {match['profile_error']}")
    if match["missing_rule_components"]:
        lines.append(
            "    componentes ausentes: "
            + ", ".join(match["missing_rule_components"])
        )
    if not match["profile_project_consistent"]:
        lines.append(
            "    motivo: profile.json declara project_name="
            f"{match['profile_project_name']}."
        )
    if not match["status_eligible"]:
        lines.append(
            "    motivo: status fora dos elegiveis para processamento."
        )
    if match.get("force"):
        lines.append("    request: processamento forcado.")
    if match.get("source_path_overridden"):
        lines.append("    request: caminho de origem sobrescrito por parametro.")
    if not match["source_exists"]:
        lines.append("    motivo: caminho de origem ausente ou inexistente.")
    if not match["found_rule_profile"]:
        lines.append("    motivo: perfil de regras nao encontrado.")
    return lines


__all__ = [
    "diagnose_ingest_theme",
    "format_ingest_theme_diagnostic",
    "format_ingest_theme_match",
]
