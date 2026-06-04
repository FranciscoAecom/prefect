import os
from dataclasses import dataclass

from core.ingest.diagnostics import (
    diagnose_ingest_theme,
    format_ingest_theme_diagnostic,
)
from core.ingest.loader import load_processing_queue
from core.ingest.run_request import IngestRunRequest
from core.queue.filters import QueueFilter
from core.queue.issue_report import export_queue_issues_report
from core.queue.summary import log_queue_summary
from core.utils import log


@dataclass(frozen=True)
class QueueRunContext:
    records: list
    output_dir: str


def prepare_processing_queue(
    output_base,
    theme_folders=None,
    queue_filter=None,
    source_path_overrides=None,
    run_request=None,
    force=False,
):
    run_request = run_request or IngestRunRequest.from_legacy(
        theme_folders=theme_folders,
        queue_filter=queue_filter,
        source_path_overrides=source_path_overrides,
        force=force,
    )
    try:
        processing_queue, queue_issues, queue_summary = load_processing_queue(
            run_request=run_request,
        )
    except Exception as exc:
        log(f"Erro ao carregar a fila ingest: {exc}")
        return None

    log_queue_summary(queue_summary, queue_issues)
    _export_queue_issues(output_base, queue_issues)

    if not processing_queue:
        log("Nenhum arquivo elegivel encontrado para iniciar a esteira.")
        log_empty_queue_diagnostics(run_request=run_request)
        return None

    output_dir = str(output_base)
    if not all(getattr(record, "output_dir", "") for record in processing_queue):
        os.makedirs(output_dir, exist_ok=True)
    return QueueRunContext(records=processing_queue, output_dir=output_dir)


TreatmentQueueRunContext = QueueRunContext
prepare_treatment_queue = prepare_processing_queue


def _export_queue_issues(output_base, queue_issues):
    if not queue_issues:
        return
    report_path = export_queue_issues_report(queue_issues, output_base)
    if report_path:
        log(f"Relatorio de issues da fila ingest gerado: {report_path}")


def log_empty_queue_diagnostics(theme_folders=None, queue_filter=None, run_request=None):
    run_request = run_request or IngestRunRequest.from_legacy(
        theme_folders=theme_folders,
        queue_filter=queue_filter,
    )
    effective_filter = run_request.queue_filter
    if not effective_filter.theme_folders:
        return

    log("Diagnostico dos filtros solicitados:")
    for theme_folder in sorted(effective_filter.theme_folders):
        diagnostic = diagnose_ingest_theme(theme_folder, run_request=run_request)
        for line in format_ingest_theme_diagnostic(diagnostic):
            log(f"  {line}")
