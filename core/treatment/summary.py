from core.utils import log
from settings import INGEST_PROCESSING_STATUSES, INGEST_SHEET_NAME, INGEST_WORKBOOK_PATH


def log_queue_summary(summary, issues):
    log("Resumo da planilha ingest:")
    log(f"  Aba analisada: {INGEST_SHEET_NAME}")
    log(f"  Caminho da planilha: {INGEST_WORKBOOK_PATH}")
    log(f"  Registros lidos: {summary['total_records']}")
    log(f"  Status elegiveis: {_format_processing_statuses(summary)}")
    log(f"  Registros com status elegivel: {summary['ready_candidates']}")
    log(f"  Arquivos aptos para processamento: {summary['eligible_records']}")
    log(f"  Registros ignorados com excecao: {summary['issues']}")

    if issues:
        log("Excecoes encontradas na fila ingest:")
        for issue in issues:
            log(
                "  "
                f"Linha {issue.sheet_row} | ID={issue.record_id} | "
                f"theme_folder={issue.theme_folder or '<vazio>'} | "
                f"{_format_issue_code(issue)}"
                f"motivo={issue.reason}"
            )


def _format_processing_statuses(summary):
    statuses = summary.get("processing_statuses") or INGEST_PROCESSING_STATUSES
    return ", ".join(str(status) for status in statuses)


def _format_issue_code(issue):
    code = getattr(issue, "code", "")
    if not code:
        return ""
    return f"codigo={code} | "
