import os
from dataclasses import dataclass

from core.ingest.diagnostics import (
    diagnose_ingest_theme,
    format_ingest_theme_diagnostic,
)
from core.ingest.loader import load_treatment_records
from core.ingest.run_request import IngestRunRequest
from core.ingest.filters import ThemeFolderFilter
from core.reporting.treatment_issues import export_treatment_issues_report
from core.treatment.summary import log_treatment_summary
from core.utils import log


@dataclass(frozen=True)
class TreatmentRunContext:
    records: list
    output_dir: str


def prepare_treatment_run(
    output_base,
    theme_folders=None,
    theme_filter=None,
    source_path_overrides=None,
    run_request=None,
    force=False,
    scheduled=False,
):
    run_request = run_request or IngestRunRequest.from_parameters(
        theme_folders=theme_folders,
        theme_filter=theme_filter,
        source_path_overrides=source_path_overrides,
        force=force,
        scheduled=scheduled,
    )
    try:
        treatment_records, treatment_issues, treatment_summary = load_treatment_records(
            run_request=run_request,
        )
    except Exception as exc:
        log(f"Erro ao carregar registros de tratamento da ingest: {exc}")
        return None

    log_treatment_summary(treatment_summary, treatment_issues)
    _export_treatment_issues(output_base, treatment_issues)

    if not treatment_records:
        log("Nenhum arquivo elegivel encontrado para iniciar o tratamento.")
        log_empty_treatment_diagnostics(run_request=run_request)
        return None

    output_dir = str(output_base)
    if not all(getattr(record, "output_dir", "") for record in treatment_records):
        os.makedirs(output_dir, exist_ok=True)
    return TreatmentRunContext(records=treatment_records, output_dir=output_dir)


def _export_treatment_issues(output_base, treatment_issues):
    if not treatment_issues:
        return
    report_path = export_treatment_issues_report(treatment_issues, output_base)
    if report_path:
        log(f"Relatorio de issues do tratamento gerado: {report_path}")


def log_empty_treatment_diagnostics(theme_folders=None, theme_filter=None, run_request=None):
    run_request = run_request or IngestRunRequest.from_parameters(
        theme_folders=theme_folders,
        theme_filter=theme_filter,
    )
    effective_filter = run_request.theme_filter
    if not effective_filter.theme_folders:
        return

    log("Diagnostico dos filtros solicitados:")
    for theme_folder in sorted(effective_filter.theme_folders):
        diagnostic = diagnose_ingest_theme(theme_folder, run_request=run_request)
        for line in format_ingest_theme_diagnostic(diagnostic):
            log(f"  {line}")


__all__ = [
    "TreatmentRunContext",
    "log_empty_treatment_diagnostics",
    "prepare_treatment_run",
]
