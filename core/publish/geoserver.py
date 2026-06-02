import json
from pathlib import Path

from core.publish.geoserver_attributes import (
    convert_geoserver_binding,
    get_geoserver_attribute_types,
)
from core.publish.geoserver_commands import (
    curl_base_command,
    data_upload_command,
    default_style_command,
    feature_type_command,
    layer_title_command,
    style_create_command,
    style_update_command,
)
from core.publish.geoserver_http import (
    add_windows_schannel_ssl_option,
    basic_auth,
    mask_sensitive_arguments,
    run_curl,
    run_curl_with_stdin,
)
from core.publish.sld import prepare_sld_for_upload, sld_content_type
from core.utils import log


def publish_to_geoserver(item, config, credentials, dry_run=False, skip_data=False):
    auth = basic_auth(credentials.geoserver_username, credentials.geoserver_password)
    upload_data_to_geoserver(item, config, auth, dry_run=dry_run, skip_data=skip_data)
    set_layer_title(item, config, auth, dry_run=dry_run)
    publish_style(item, config, auth, dry_run=dry_run)
    set_default_style(item, config, auth, dry_run=dry_run)
    if item.layer_resource == "featuretypes" and not dry_run:
        return get_geoserver_attribute_types(item, config, auth)
    return {}


def upload_data_to_geoserver(item, config, auth, dry_run=False, skip_data=False):
    if skip_data:
        log("1/5 - Upload de dados ignorado por configuracao.")
        return
    log(f"1/5 - Publicando {item.data_label} no GeoServer: {item.layer}")
    run_curl(data_upload_command(item, config, auth), dry_run=dry_run)


def set_layer_title(item, config, auth, dry_run=False):
    log(f"2/5 - Ajustando titulo da camada: {item.layer}")
    resource = "featureType" if item.layer_resource == "featuretypes" else "coverage"
    body = f'<?xml version="1.0" encoding="UTF-8"?><{resource}><title>{xml_escape(item.layer_title)}</title></{resource}>'
    run_curl_with_stdin(layer_title_command(item, config, auth), body, dry_run=dry_run)


def publish_style(item, config, auth, dry_run=False):
    log(f"3/5 - Criando ou atualizando estilo SLD: {item.style}")
    upload_sld = prepare_sld_for_upload(item.sld_path, item.style, item.layer)
    content_type = sld_content_type(upload_sld)
    try:
        create_or_update_style(item, config, auth, upload_sld, content_type, dry_run)
    finally:
        if upload_sld != Path(item.sld_path):
            upload_sld.unlink(missing_ok=True)


def set_default_style(item, config, auth, dry_run=False):
    log(f"4/5 - Associando estilo a camada: {item.layer}")
    body = json.dumps(
        {"layer": {"defaultStyle": {"name": item.style, "workspace": config.workspace}}}
    )
    run_curl_with_stdin(default_style_command(item, config, auth), body, dry_run=dry_run)


def create_or_update_style(item, config, auth, upload_sld, content_type, dry_run=False):
    try:
        run_curl(style_create_command(item, config, auth, upload_sld, content_type), dry_run=dry_run)
    except RuntimeError:
        run_curl(style_update_command(item, config, auth, upload_sld, content_type), dry_run=dry_run)


def xml_escape(text):
    return (
        str(text)
        .replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
        .replace('"', "&quot;")
        .replace("'", "&apos;")
    )


__all__ = [
    "add_windows_schannel_ssl_option",
    "basic_auth",
    "convert_geoserver_binding",
    "create_or_update_style",
    "curl_base_command",
    "data_upload_command",
    "default_style_command",
    "feature_type_command",
    "get_geoserver_attribute_types",
    "layer_title_command",
    "mask_sensitive_arguments",
    "publish_style",
    "publish_to_geoserver",
    "run_curl",
    "run_curl_with_stdin",
    "set_default_style",
    "set_layer_title",
    "style_create_command",
    "style_update_command",
    "upload_data_to_geoserver",
    "xml_escape",
]
