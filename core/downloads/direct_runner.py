from pathlib import Path

from core.downloads.config import DownloadRunOptions
from core.flow.publish import publish_record_outputs_direct
from core.utils import log


def run_download_publish_direct(
    source_root=None,
    output_dir=None,
    extract_base=None,
    output_base=None,
    force=False,
    emit_download_event=False,
    treatment_after_download=True,
    publish_after_treatment=True,
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
    from core.flow.downloads import build_download_flow_options
    from core.tasks.downloads import load_download_records_task

    records = load_download_records_task.fn(theme_folders=theme_folders)
    if not records:
        log("Nenhum registro elegivel para download.")
        return []

    options = build_download_flow_options(
        source_root=source_root,
        output_dir=output_dir,
        extract_base=extract_base,
        output_base=output_base,
        force=force,
        emit_download_event=emit_download_event,
        treatment_after_download=treatment_after_download,
        publish_after_treatment=publish_after_treatment,
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
    publish_options = options.publish
    config = publish_options.build_config()
    credentials = publish_options.load_credentials()

    results = []
    for record in records:
        extracted = run_single_download_direct(
            record=record,
            dataset_key=record["dataset_key"],
            region=record["region"],
            run_options=options.run,
        )
        if options.run.publish_after_treatment:
            publish_record_outputs_direct(
                extracted["silver_dir"],
                config,
                credentials,
                **publish_options.execution_kwargs(),
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
    treatment_after_download=True,
    run_options=None,
):
    from core.tasks.downloads import (
        download_dataset_task,
        emit_dataset_downloaded_event_task,
        extract_download_task,
        resolve_download_version_plan_task,
    )

    run_options = run_options or DownloadRunOptions(
        source_root=source_root,
        output_dir=output_dir,
        extract_base=extract_base,
        output_base=output_base,
        force=force,
        emit_download_event=emit_download_event,
        treatment_after_download=treatment_after_download,
    )
    version_plan = resolve_download_version_plan_task.fn(record)
    temp_dir = Path(version_plan["temp_dir"])
    archive_output_dir = (
        Path(run_options.output_dir) if run_options.output_dir else temp_dir / "_downloads"
    )
    extract_dir = temp_dir / "raw"

    downloaded = download_dataset_task.fn(
        dataset_key=dataset_key,
        region=region,
        source_root=run_options.source_root,
        output_dir=str(archive_output_dir),
        force=run_options.force,
    )
    extracted = extract_download_task.fn(
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
        emit_dataset_downloaded_event_task.fn(extracted)

    return extracted


__all__ = ["run_download_publish_direct", "run_single_download_direct"]
