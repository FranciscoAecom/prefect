from pathlib import Path

import pandas as pd

from core.ingest.normalization import normalize_status, normalize_theme_folder, stringify
from core.rules.engine import (
    RuleProfileResolutionError,
    expected_rule_profile_name,
    find_rule_profile_by_theme_folder,
)
from projects.configs import resolve_project_name
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
):
    target_theme = normalize_theme_folder(theme_folder)
    ready_statuses = {normalize_status(status) for status in ready_status}
    dataframe = pd.read_excel(workbook_path, sheet_name=sheet_name)
    matches = []

    for idx, row in dataframe.iterrows():
        row_theme_folder = stringify(row.get("theme_folder"))
        if normalize_theme_folder(row_theme_folder) != target_theme:
            continue

        status = stringify(row.get("status"))
        source_path = stringify(row.get("path_shapefile_temp"))
        expected_profile = expected_rule_profile_name(row_theme_folder)
        try:
            found_profile = find_rule_profile_by_theme_folder(row_theme_folder)
            profile_error = ""
        except RuleProfileResolutionError as exc:
            found_profile = None
            profile_error = str(exc)

        source_exists = bool(source_path and Path(source_path).exists())
        matches.append(
            {
                "sheet_row": idx + 2,
                "record_id": row.get("ID"),
                "theme": stringify(row.get("theme")),
                "theme_folder": row_theme_folder,
                "status": status,
                "status_eligible": normalize_status(status) in ready_statuses,
                "source_path": source_path,
                "source_exists": source_exists,
                "project_name": resolve_project_name(row_theme_folder),
                "expected_rule_profile": expected_profile,
                "found_rule_profile": found_profile,
                "profile_error": profile_error,
            }
        )

    return {
        "theme_folder": theme_folder,
        "normalized_theme_folder": target_theme,
        "workbook_path": str(workbook_path),
        "sheet_name": sheet_name,
        "ready_statuses": list(ready_status),
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
    if not match["status_eligible"]:
        lines.append(
            "    motivo: status fora dos elegiveis para processamento."
        )
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
