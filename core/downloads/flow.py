from __future__ import annotations

import shutil
import zipfile
from pathlib import Path

from prefect import flow, task
from prefect.events import emit_event

from core.downloads.config import DownloadFlowOptions, DownloadRunOptions
from core.downloads.connectors.car_public_api import download_car_public_api_target
from core.downloads.catalog import get_download_target
from core.downloads.queue import load_download_queue
from core.prefect_flow import data_pipeline_flow
from core.prefect_support.variables import get_path_variable
from core.publish.flow import data_publish_flow
from core.publish.config import PublishOptions
from core.queue.filters import QueueFilter
from core.utils import log
from core.versioning import resolve_dataset_version_plan
from core.config.defaults import DEFAULT_DOWNLOAD_EXTRACT_BASE


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


@task(name="Carregar fila de downloads", log_prints=True)
def load_download_queue_task(theme_folders=None):
    records, issues, summary = load_download_queue(theme_folders=theme_folders)
    log_download_queue_summary(summary, issues)
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


def log_download_queue_summary(summary, issues):
    log("Resumo da fila de downloads:")
    log(f"  Registros lidos: {summary['total_records']}")
    log(f"  Status elegivel: {summary['download_status']}")
    log(f"  Registros com status elegivel: {summary['download_candidates']}")
    log(f"  Registros aptos para download: {summary['eligible_records']}")
    log(f"  Registros ignorados com excecao: {summary['issues']}")
    if issues:
        log("Excecoes encontradas na fila de downloads:")
        for issue in issues:
            log(
                "  Linha "
                f"{issue.sheet_row} | ID={issue.record_id} | "
                f"theme_folder={issue.theme_folder} | motivo: {issue.reason}"
            )


def data_download_flow_run_name():
    from prefect.runtime import flow_run

    parameters = flow_run.parameters or {}
    theme_folders = sorted(
        QueueFilter.from_theme_folders(parameters.get("theme_folders")).theme_folders
    )
    if len(theme_folders) == 1:
        return f"download_{theme_folders[0]}"
    if theme_folders:
        return f"download_{len(theme_folders)}_bases"
    return "download_ingest"


@flow(name="Data Download", flow_run_name=data_download_flow_run_name, log_prints=True)
def data_download_flow(
    source_root=None,
    output_dir=None,
    extract_base=None,
    output_base=None,
    force=False,
    emit_download_event=True,
    process_after_download=True,
    publish_after_process=False,
    publish_environment="qas",
    publish_workspace="gold",
    publish_geoserver=None,
    publish_catalog=None,
    publish_catalog_group="2",
    publish_catalog_category="2",
    publish_data_dictionary_base_url=None,
    publish_same_credential_for_catalog=True,
    publish_geoserver_username=None,
    publish_geoserver_password=None,
    publish_geonetwork_username=None,
    publish_geonetwork_password=None,
    publish_dry_run=False,
    publish_skip_geoserver=False,
    publish_skip_data=False,
    publish_skip_catalog=False,
    theme_folders=None,
):
    options = build_download_flow_options(
        source_root=source_root,
        output_dir=output_dir,
        extract_base=extract_base,
        output_base=output_base,
        force=force,
        emit_download_event=emit_download_event,
        process_after_download=process_after_download,
        publish_after_process=publish_after_process,
        publish_environment=publish_environment,
        publish_workspace=publish_workspace,
        publish_geoserver=publish_geoserver,
        publish_catalog=publish_catalog,
        publish_catalog_group=publish_catalog_group,
        publish_catalog_category=publish_catalog_category,
        publish_data_dictionary_base_url=publish_data_dictionary_base_url,
        publish_same_credential_for_catalog=publish_same_credential_for_catalog,
        publish_geoserver_username=publish_geoserver_username,
        publish_geoserver_password=publish_geoserver_password,
        publish_geonetwork_username=publish_geonetwork_username,
        publish_geonetwork_password=publish_geonetwork_password,
        publish_dry_run=publish_dry_run,
        publish_skip_geoserver=publish_skip_geoserver,
        publish_skip_data=publish_skip_data,
        publish_skip_catalog=publish_skip_catalog,
    )
    records = load_download_queue_task(theme_folders=theme_folders)
    if not records:
        log("Nenhum registro elegivel para download.")
        return []

    results = []
    for record in records:
        results.append(
            _run_single_download(
                record=record,
                dataset_key=record["dataset_key"],
                region=record["region"],
                run_options=options.run,
                publish_options=options.publish,
            )
        )
    return results


def build_download_flow_options(
    source_root=None,
    output_dir=None,
    extract_base=None,
    output_base=None,
    force=False,
    emit_download_event=True,
    process_after_download=True,
    publish_after_process=False,
    publish_environment="qas",
    publish_workspace="gold",
    publish_geoserver=None,
    publish_catalog=None,
    publish_catalog_group="2",
    publish_catalog_category="2",
    publish_data_dictionary_base_url=None,
    publish_same_credential_for_catalog=True,
    publish_geoserver_username=None,
    publish_geoserver_password=None,
    publish_geonetwork_username=None,
    publish_geonetwork_password=None,
    publish_dry_run=False,
    publish_skip_geoserver=False,
    publish_skip_data=False,
    publish_skip_catalog=False,
):
    return DownloadFlowOptions(
        run=DownloadRunOptions(
            source_root=source_root,
            output_dir=output_dir,
            extract_base=extract_base,
            output_base=output_base,
            force=force,
            emit_download_event=emit_download_event,
            process_after_download=process_after_download,
            publish_after_process=publish_after_process,
        ),
        publish=PublishOptions(
            environment=publish_environment,
            workspace=publish_workspace,
            geoserver=publish_geoserver,
            catalog=publish_catalog,
            catalog_group=publish_catalog_group,
            catalog_category=publish_catalog_category,
            data_dictionary_base_url=publish_data_dictionary_base_url,
            same_credential_for_catalog=publish_same_credential_for_catalog,
            geoserver_username=publish_geoserver_username,
            geoserver_password=publish_geoserver_password,
            geonetwork_username=publish_geonetwork_username,
            geonetwork_password=publish_geonetwork_password,
            dry_run=publish_dry_run,
            skip_geoserver=publish_skip_geoserver,
            skip_data=publish_skip_data,
            skip_catalog=publish_skip_catalog,
        ),
    )


def _run_single_download(
    record,
    dataset_key,
    region,
    run_options=None,
    publish_options=None,
):
    run_options = run_options or DownloadRunOptions()
    version_plan = resolve_download_version_plan_task(record)
    temp_dir = Path(version_plan["temp_dir"])
    archive_output_dir = (
        Path(run_options.output_dir) if run_options.output_dir else temp_dir / "_downloads"
    )
    extract_dir = temp_dir / "raw"

    downloaded = download_dataset_task(
        dataset_key=dataset_key,
        region=region,
        source_root=run_options.source_root,
        output_dir=str(archive_output_dir),
        force=run_options.force,
    )
    extracted = extract_download_task(
        downloaded,
        extract_base=run_options.extract_base,
        extract_dir=str(extract_dir),
    )
    extracted = {
        **extracted,
        "version": version_plan["version"],
        "temp_dir": version_plan["temp_dir"],
        "bronze_dir": version_plan["bronze_dir"],
        "silver_dir": version_plan["silver_dir"],
    }

    if run_options.emit_download_event:
        emit_dataset_downloaded_event_task(extracted)

    if run_options.process_after_download:
        data_pipeline_flow(
            output_base=run_options.output_base,
            theme_folders=[extracted["theme_folder"]],
            source_path_overrides={
                extracted["theme_folder"]: extracted["extract_dir"],
            },
        )

    if run_options.publish_after_process:
        publish_options = publish_options or PublishOptions()
        data_publish_flow(
            folder=extracted["silver_dir"],
            **publish_options.task_kwargs(),
        )

    return extracted


def run_download_publish_direct(*args, **kwargs):
    from core.downloads.direct_runner import run_download_publish_direct as run_direct

    return run_direct(*args, **kwargs)


__all__ = [
    "build_download_flow_options",
    "data_download_flow",
    "run_download_publish_direct",
]
