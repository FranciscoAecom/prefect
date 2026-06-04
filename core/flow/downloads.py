from prefect import flow

from core.downloads.config import DownloadFlowOptions, DownloadRunOptions
from core.downloads.service import run_data_download
from core.ingest.filters import QueueFilter
from core.publish.config import PublishOptions
from core.tasks.downloads import load_download_queue_task


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
    process_after_download=False,
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
    return run_data_download(records, run_options=options.run)


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


def run_download_publish_direct(*args, **kwargs):
    from core.downloads.direct_runner import run_download_publish_direct as run_direct

    return run_direct(*args, **kwargs)


__all__ = [
    "build_download_flow_options",
    "data_download_flow",
    "data_download_flow_run_name",
    "run_download_publish_direct",
]
