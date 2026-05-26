import os
from dataclasses import dataclass

from core.ingest.diagnostics import (
    diagnose_ingest_theme,
    format_ingest_theme_diagnostic,
)
from core.ingest.loader import load_processing_queue
from core.queue.filters import QueueFilter
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
):
    try:
        processing_queue, queue_issues, queue_summary = load_processing_queue(
            theme_folders=theme_folders,
            queue_filter=queue_filter,
            source_path_overrides=source_path_overrides,
        )
    except Exception as exc:
        log(f"Erro ao carregar a fila ingest: {exc}")
        return None

    log_queue_summary(queue_summary, queue_issues)

    if not processing_queue:
        log("Nenhum arquivo elegivel encontrado para iniciar a esteira.")
        log_empty_queue_diagnostics(theme_folders, queue_filter)
        return None

    output_dir = str(output_base)
    if not all(getattr(record, "output_dir", "") for record in processing_queue):
        os.makedirs(output_dir, exist_ok=True)
    return QueueRunContext(records=processing_queue, output_dir=output_dir)


def log_empty_queue_diagnostics(theme_folders=None, queue_filter=None):
    effective_filter = queue_filter or QueueFilter.from_theme_folders(theme_folders)
    if not effective_filter.theme_folders:
        return

    log("Diagnostico dos filtros solicitados:")
    for theme_folder in sorted(effective_filter.theme_folders):
        diagnostic = diagnose_ingest_theme(theme_folder)
        for line in format_ingest_theme_diagnostic(diagnostic):
            log(f"  {line}")
