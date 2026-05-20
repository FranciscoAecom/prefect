from __future__ import annotations

import shutil
import zipfile
from pathlib import Path

from prefect import flow, task
from prefect.events import emit_event

from core.downloads.car_api import download_car_api_target
from core.downloads.catalog import get_download_target, resolve_theme_folder
from core.prefect_flow import data_pipeline_flow
from core.utils import log
from settings import DOWNLOAD_EXTRACT_BASE


@task(name="Baixar dataset", log_prints=True)
def download_dataset_task(
    dataset_key,
    region,
    source_root=None,
    output_dir=None,
    force=False,
):
    target = get_download_target(dataset_key)
    if target.connector == "car_api":
        return download_car_api_target(
            target,
            region,
            api_car_root=source_root,
            output_dir=output_dir,
            force=force,
        )
    raise ValueError(f"Conector de download nao implementado: {target.connector}")


@task(name="Extrair dataset", log_prints=True)
def extract_download_task(download_result, extract_base=None):
    archive_path = Path(download_result["archive_path"])
    theme_folder = download_result["theme_folder"]
    extract_root = Path(extract_base or DOWNLOAD_EXTRACT_BASE)
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
    if download_result["connector"] == "car_api":
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


def data_download_flow_run_name():
    from prefect.runtime import flow_run

    parameters = flow_run.parameters or {}
    try:
        target = get_download_target(parameters.get("dataset_key", "car_uso_restrito"))
        theme_folder = resolve_theme_folder(
            target,
            parameters.get("region") or target.default_region or "MG",
        )
    except ValueError:
        return "download_dataset"
    return f"download_{theme_folder}"


@flow(name="Data Download", flow_run_name=data_download_flow_run_name, log_prints=True)
def data_download_flow(
    dataset_key="car_uso_restrito",
    region="MG",
    source_root=None,
    output_dir=None,
    extract_base=None,
    output_base=None,
    force=False,
    emit_download_event=True,
    process_after_download=True,
):
    downloaded = download_dataset_task(
        dataset_key=dataset_key,
        region=region,
        source_root=source_root,
        output_dir=output_dir,
        force=force,
    )
    extracted = extract_download_task(downloaded, extract_base=extract_base)

    if emit_download_event:
        emit_dataset_downloaded_event_task(extracted)

    if process_after_download:
        data_pipeline_flow(
            output_base=output_base,
            theme_folders=[extracted["theme_folder"]],
            source_path_overrides={
                extracted["theme_folder"]: extracted["extract_dir"],
            },
        )

    return extracted


__all__ = ["data_download_flow"]
