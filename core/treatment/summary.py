from core.reporting.log_summary import format_ingest_issue, log_summary
from settings import INGEST_TREATMENT_STATUSES, INGEST_SHEET_NAME, INGEST_WORKBOOK_PATH


def log_treatment_summary(summary, issues):
    log_summary(
        "Resumo da planilha ingest",
        [
            ("Aba analisada", INGEST_SHEET_NAME),
            ("Caminho da planilha", INGEST_WORKBOOK_PATH),
            ("Registros lidos", summary["total_records"]),
            ("Status elegiveis", _format_treatment_statuses(summary)),
            ("Registros com status elegivel", summary["ready_candidates"]),
            ("Arquivos aptos para tratamento", summary["eligible_records"]),
            ("Registros ignorados com excecao", summary["issues"]),
        ],
        issues_title="Excecoes encontradas para tratamento",
        issues=issues,
        format_issue=format_ingest_issue,
    )


def _format_treatment_statuses(summary):
    statuses = summary.get("treatment_statuses") or INGEST_TREATMENT_STATUSES
    return ", ".join(str(status) for status in statuses)

