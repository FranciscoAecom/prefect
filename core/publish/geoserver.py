import base64
import json
import subprocess
from pathlib import Path

import core.publish.urls as urls
from core.publish.sld import prepare_sld_for_upload
from core.utils import log


def publish_to_geoserver(item, config, credentials, dry_run=False, skip_data=False):
    auth = basic_auth(credentials.geoserver_username, credentials.geoserver_password)
    if skip_data:
        log("1/5 - Upload de dados ignorado por configuracao.")
    else:
        log(f"1/5 - Publicando {item.data_label} no GeoServer: {item.layer}")
        run_curl(
            [
                "--fail-with-body",
                "--show-error",
                "--location",
                "--retry",
                "3",
                "--retry-delay",
                "10",
                "--connect-timeout",
                "60",
                "--max-time",
                "0",
                "--request",
                "PUT",
                "--header",
                f"Authorization: Basic {auth}",
                "--header",
                f"Content-Type: {item.data_content_type}",
                "--upload-file",
                str(item.data_path),
                urls.geoserver_data_upload_url(
                    config.geoserver,
                    config.workspace,
                    item.data_endpoint,
                    item.store,
                    item.data_type,
                ),
            ],
            dry_run=dry_run,
        )

    set_layer_title(item, config, auth, dry_run=dry_run)
    publish_style(item, config, auth, dry_run=dry_run)
    set_default_style(item, config, auth, dry_run=dry_run)


def set_layer_title(item, config, auth, dry_run=False):
    log(f"2/5 - Ajustando titulo da camada: {item.layer}")
    resource = "featureType" if item.layer_resource == "featuretypes" else "coverage"
    body = f'<?xml version="1.0" encoding="UTF-8"?><{resource}><title>{xml_escape(item.layer_title)}</title></{resource}>'
    run_curl_with_stdin(
        [
            "--fail-with-body",
            "--show-error",
            "--location",
            "--retry",
            "3",
            "--retry-delay",
            "5",
            "--connect-timeout",
            "60",
            "--max-time",
            "0",
            "--request",
            "PUT",
            "--header",
            f"Authorization: Basic {auth}",
            "--header",
            "Content-Type: application/xml; charset=UTF-8",
            "--data-binary",
            "@-",
            urls.geoserver_layer_resource_url(
                config.geoserver,
                config.workspace,
                item.data_endpoint,
                item.store,
                item.layer_resource,
                item.layer,
            ),
        ],
        body,
        dry_run=dry_run,
    )


def publish_style(item, config, auth, dry_run=False):
    log(f"3/5 - Criando ou atualizando estilo SLD: {item.style}")
    upload_sld = prepare_sld_for_upload(item.sld_path, item.style, item.layer)
    try:
        try:
            run_curl(
                [
                    "--fail-with-body",
                    "--show-error",
                    "--location",
                    "--retry",
                    "3",
                    "--retry-delay",
                    "5",
                    "--connect-timeout",
                    "60",
                    "--max-time",
                    "0",
                    "--request",
                    "POST",
                    "--header",
                    f"Authorization: Basic {auth}",
                    "--header",
                    "Content-Type: application/vnd.ogc.sld+xml",
                    "--data-binary",
                    f"@{upload_sld}",
                    urls.geoserver_style_collection_url(
                        config.geoserver,
                        config.workspace,
                        item.style,
                    ),
                ],
                dry_run=dry_run,
            )
        except RuntimeError:
            run_curl(
                [
                    "--fail-with-body",
                    "--show-error",
                    "--location",
                    "--retry",
                    "3",
                    "--retry-delay",
                    "5",
                    "--connect-timeout",
                    "60",
                    "--max-time",
                    "0",
                    "--request",
                    "PUT",
                    "--header",
                    f"Authorization: Basic {auth}",
                    "--header",
                    "Content-Type: application/vnd.ogc.sld+xml",
                    "--data-binary",
                    f"@{upload_sld}",
                    urls.geoserver_style_url(
                        config.geoserver,
                        config.workspace,
                        item.style,
                    ),
                ],
                dry_run=dry_run,
            )
    finally:
        if upload_sld != Path(item.sld_path):
            upload_sld.unlink(missing_ok=True)


def set_default_style(item, config, auth, dry_run=False):
    log(f"4/5 - Associando estilo a camada: {item.layer}")
    body = json.dumps(
        {
            "layer": {
                "defaultStyle": {
                    "name": item.style,
                    "workspace": config.workspace,
                }
            }
        }
    )
    run_curl_with_stdin(
        [
            "--fail-with-body",
            "--show-error",
            "--location",
            "--retry",
            "3",
            "--retry-delay",
            "5",
            "--connect-timeout",
            "60",
            "--max-time",
            "0",
            "--request",
            "PUT",
            "--header",
            f"Authorization: Basic {auth}",
            "--header",
            "Content-Type: application/json",
            "--data-binary",
            "@-",
            urls.geoserver_layer_url(config.geoserver, config.workspace, item.layer),
        ],
        body,
        dry_run=dry_run,
    )


def basic_auth(username, password):
    token = f"{username}:{password}".encode("ascii")
    return base64.b64encode(token).decode("ascii")


def run_curl(arguments, dry_run=False, capture=False):
    arguments = add_windows_schannel_ssl_option(arguments)
    display = mask_sensitive_arguments(arguments)
    log("curl.exe " + " ".join(display))
    if dry_run:
        log("DRY-RUN: curl.exe nao executado.")
        return ""
    result = subprocess.run(
        ["curl.exe", *arguments],
        check=False,
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        output = (result.stdout or "") + (result.stderr or "")
        raise RuntimeError(f"curl.exe falhou com exit code {result.returncode}: {output}")
    return result.stdout if capture else ""


def run_curl_with_stdin(arguments, stdin_text, dry_run=False):
    arguments = add_windows_schannel_ssl_option(arguments)
    display = mask_sensitive_arguments(arguments)
    log("curl.exe " + " ".join(display))
    if dry_run:
        log("DRY-RUN: curl.exe nao executado.")
        return
    result = subprocess.run(
        ["curl.exe", *arguments],
        input=stdin_text,
        text=True,
        check=False,
        capture_output=True,
    )
    if result.returncode != 0:
        output = (result.stdout or "") + (result.stderr or "")
        raise RuntimeError(f"curl.exe falhou com exit code {result.returncode}: {output}")


def mask_sensitive_arguments(arguments):
    masked = []
    skip_next = False
    for index, argument in enumerate(arguments):
        if skip_next:
            skip_next = False
            continue
        if argument == "--header" and index + 1 < len(arguments):
            next_arg = arguments[index + 1]
            if next_arg.startswith("Authorization: Basic "):
                masked.extend(["--header", "Authorization: Basic ***"])
                skip_next = True
                continue
            if next_arg.startswith("X-XSRF-TOKEN: "):
                masked.extend(["--header", "X-XSRF-TOKEN: ***"])
                skip_next = True
                continue
        masked.append(str(argument))
    return masked


def add_windows_schannel_ssl_option(arguments):
    if "--ssl-no-revoke" in arguments:
        return arguments
    if not any(str(argument).lower().startswith("https://") for argument in arguments):
        return arguments
    return ["--ssl-no-revoke", *arguments]


def xml_escape(text):
    return (
        str(text)
        .replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
        .replace('"', "&quot;")
        .replace("'", "&apos;")
    )
