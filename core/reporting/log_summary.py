from core.utils import log


def log_summary(title, rows, issues_title=None, issues=None, format_issue=None):
    log(f"{title}:")
    for label, value in rows:
        log(f"  {label}: {value}")

    if issues:
        log(f"{issues_title or 'Excecoes encontradas'}:")
        formatter = format_issue or str
        for issue in issues:
            log(formatter(issue))


def format_ingest_issue(issue):
    return (
        "  "
        f"Linha {issue.sheet_row} | ID={issue.record_id} | "
        f"theme_folder={getattr(issue, 'theme_folder', '') or '<vazio>'} | "
        f"{format_issue_code(issue)}"
        f"motivo={issue.reason}"
    )


def format_issue_code(issue):
    code = getattr(issue, "code", "")
    if not code:
        return ""
    return f"codigo={code} | "


__all__ = ["format_ingest_issue", "format_issue_code", "log_summary"]
