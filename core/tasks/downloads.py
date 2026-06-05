import shutil
import zipfile
from pathlib import Path

from prefect import task
from prefect.events import emit_event

from core.config.defaults import DEFAULT_DOWNLOAD_EXTRACT_BASE
from core.downloads.catalog import get_download_target
from core.downloads.connectors.car_public_api import download_car_public_api_target
from core.downloads.records import load_download_records
from core.prefect_support.variables import get_path_variable
from core.reporting.log_summary import log_summary
from core.utils import log
from core.versioning import resolve_dataset_version_plan


@task(name="Baixar dataset", log_prints=True)
def download_dataset_task(
    dataset_key,
    region,
    source_root=None,
    output_dir=None,
    force=False,
):
    target = get_download_target(dataset_key)
    if target.connector == "car_public_api":
        return download_car_public_api_target(
            target,
            region,
            api_base=source_root,
            output_dir=output_dir,
            force=force,
        )
    raise ValueError(f"Conector de download nao implementado: {target.connector}")


@task(name="Extrair dataset", log_prints=True)
def extract_download_task(download_result, extract_base=None, extract_dir=None):
    archive_path = Path(download_result["archive_path"])
    theme_folder = download_result["theme_folder"]
    if extract_dir:
        extract_dir = Path(extract_dir)
    else:
        extract_root = Path(extract_base) if extract_base else get_path_variable(
            "download_extract_base",
            DEFAULT_DOWNLOAD_EXTRACT_BASE,
        )
        extract_dir = extract_root / theme_folder

    if extract_dir.exists():
        shutil.rmtree(extract_dir)
    extract_dir.mkdir(parents=True, exist_ok=True)

    log(f"Extraindo {archive_path} para {extract_dir}")
    if archive_path.suffix.lower() == ".zip":
        with zipfile.ZipFile(archive_path) as archive:
            archive.extractall(extract_dir)
    else:
        shutil.copy2(archive_path, extract_dir / archive_path.name)

    result = dict(download_result)
    result["extract_dir"] = str(extract_dir)
    return result


@task(name="Emitir evento dataset baixado", log_prints=True)
def emit_dataset_downloaded_event_task(download_result):
    theme_folder = download_result["theme_folder"]
    payload = {
        "dataset_key": download_result["dataset_key"],
        "theme_folders": [theme_folder],
        "source_path_overrides": {theme_folder: download_result["extract_dir"]},
        "archive_path": download_result["archive_path"],
        "extract_dir": download_result["extract_dir"],
    }
    event = emit_event(
        event="dataset.downloaded",
        resource={
            "prefect.resource.id": f"dataset.{theme_folder}",
            "prefect.resource.name": theme_folder,
            "dataset.key": download_result["dataset_key"],
            "dataset.connector": download_result["connector"],
            "dataset.region": download_result.get("region", ""),
        },
        payload=payload,
    )
    if download_result["connector"] == "car_public_api":
        emit_event(
            event="car.downloaded",
            resource={
                "prefect.resource.id": f"car.{theme_folder}",
                "prefect.resource.name": theme_folder,
                "car.theme_code": download_result["car_theme_code"],
                "car.uf": download_result.get("region", ""),
            },
            payload={
                **payload,
                "zip_path": download_result["archive_path"],
                "theme_code": download_result["car_theme_code"],
            },
        )
    log(f"Evento dataset.downloaded emitido para {theme_folder}")
    return str(event.id) if event else None


@task(name="Carregar registros de download", log_prints=True)
def load_download_records_task(theme_folders=None):
    records, issues, summary = load_download_records(theme_folders=theme_folders)
    log_download_summary(summary, issues)
    return [record.__dict__ for record in records]


@task(name="Resolver versao do download", log_prints=True)
def resolve_download_version_plan_task(record):
    plan = resolve_dataset_version_plan(record)
    log(f"Diretorio temp do download: {plan.temp_dir}")
    log(f"Diretorio bronze planejado: {plan.bronze_dir}")
    log(f"Diretorio silver planejado: {plan.silver_dir}")
    return {
        "version": plan.version,
        "temp_dir": str(plan.temp_dir),
        "bronze_dir": str(plan.bronze_dir),
        "silver_dir": str(plan.silver_dir),
    }


def log_download_summary(summary, issues):
    log_summary(
        "Resumo dos registros de download",
        [
            ("Registros lidos", summary["total_records"]),
            ("Status elegivel", summary["download_status"]),
            ("Registros com status elegivel", summary["download_candidates"]),
            ("Registros aptos para download", summary["eligible_records"]),
            ("Registros ignorados com excecao", summary["issues"]),
        ],
        issues_title="Excecoes encontradas nos registros de download",
        issues=issues,
        format_issue=lambda issue: (
            "  Linha "
            f"{issue.sheet_row} | ID={issue.record_id} | "
            f"theme_folder={issue.theme_folder} | motivo={issue.reason}"
        ),
    )


__all__ = [
    "download_dataset_task",
    "emit_dataset_downloaded_event_task",
    "extract_download_task",
    "load_download_records_task",
    "log_download_summary",
    "resolve_download_version_plan_task",
]
