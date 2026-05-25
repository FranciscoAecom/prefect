from pathlib import Path

from core.prefect_flow import data_pipeline_flow
from core.publish.config import config_for_environment, load_publish_credentials
from core.publish.pipeline_flow import publish_record_outputs_direct
from core.utils import log


def run_download_publish_direct(
    source_root=None,
    output_dir=None,
    extract_base=None,
    output_base=None,
    force=False,
    emit_download_event=False,
    process_after_download=True,
    publish_after_process=True,
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
    from core.downloads.flow import load_download_queue_task

    records = load_download_queue_task.fn(theme_folders=theme_folders)
    if not records:
        log("Nenhum registro elegivel para download.")
        return []

    config = config_for_environment(
        publish_environment,
        geoserver=publish_geoserver,
        catalog=publish_catalog,
        workspace=publish_workspace,
        catalog_group=publish_catalog_group,
        catalog_category=publish_catalog_category,
        data_dictionary_base_url=publish_data_dictionary_base_url,
    )
    credentials = load_publish_credentials(
        same_credential_for_catalog=publish_same_credential_for_catalog,
        allow_prompt=False,
        geoserver_username=publish_geoserver_username,
        geoserver_password=publish_geoserver_password,
        geonetwork_username=publish_geonetwork_username,
        geonetwork_password=publish_geonetwork_password,
    )

    results = []
    for record in records:
        extracted = run_single_download_direct(
            record=record,
            dataset_key=record["dataset_key"],
            region=record["region"],
            source_root=source_root,
            output_dir=output_dir,
            extract_base=extract_base,
            output_base=output_base,
            force=force,
            emit_download_event=emit_download_event,
            process_after_download=process_after_download,
        )
        if publish_after_process:
            publish_record_outputs_direct(
                extracted["silver_dir"],
                config,
                credentials,
                dry_run=publish_dry_run,
                skip_geoserver=publish_skip_geoserver,
                skip_data=publish_skip_data,
                skip_catalog=publish_skip_catalog,
            )
        results.append(extracted)
    return results


def run_single_download_direct(
    record,
    dataset_key,
    region,
    source_root=None,
    output_dir=None,
    extract_base=None,
    output_base=None,
    force=False,
    emit_download_event=False,
    process_after_download=True,
):
    from core.downloads.flow import (
        download_dataset_task,
        emit_dataset_downloaded_event_task,
        extract_download_task,
        resolve_download_version_plan_task,
    )

    version_plan = resolve_download_version_plan_task.fn(record)
    temp_dir = Path(version_plan["temp_dir"])
    archive_output_dir = Path(output_dir) if output_dir else temp_dir / "_downloads"
    extract_dir = temp_dir / "raw"

    downloaded = download_dataset_task.fn(
        dataset_key=dataset_key,
        region=region,
        source_root=source_root,
        output_dir=str(archive_output_dir),
        force=force,
    )
    extracted = extract_download_task.fn(
        downloaded,
        extract_base=extract_base,
        extract_dir=str(extract_dir),
    )
    extracted = {
        **extracted,
        "version": version_plan["version"],
        "temp_dir": version_plan["temp_dir"],
        "bronze_dir": version_plan["bronze_dir"],
        "silver_dir": version_plan["silver_dir"],
    }

    if emit_download_event:
        emit_dataset_downloaded_event_task.fn(extracted)

    if process_after_download:
        data_pipeline_flow.fn(
            output_base=output_base,
            theme_folders=[extracted["theme_folder"]],
            source_path_overrides={
                extracted["theme_folder"]: extracted["extract_dir"],
            },
        )

    return extracted


__all__ = ["run_download_publish_direct", "run_single_download_direct"]
