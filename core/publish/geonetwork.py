from pathlib import Path
import tempfile

from core.publish.geoserver import basic_auth, run_curl
from core.publish.metadata import metadata_xml_with_data_dictionary_link
import core.publish.urls as urls
from core.utils import log


def import_metadata_to_geonetwork(
    item,
    config,
    credentials,
    dry_run=False,
    attribute_types=None,
):
    auth = basic_auth(credentials.catalog_username, credentials.catalog_password)
    log(f"5/5 - Importando XML no GeoNetwork: {item.xml_path.name}")
    cookie_jar = None
    metadata_upload_path = Path(item.xml_path)
    if dry_run:
        xsrf_token = "DRYRUN-XSRF-TOKEN"
    else:
        cookie_jar = tempfile.NamedTemporaryFile(delete=False)
        cookie_jar.close()
        run_curl(
            [
                "--fail-with-body",
                "--show-error",
                "--location",
                "--connect-timeout",
                "60",
                "--max-time",
                "0",
                "--cookie-jar",
                cookie_jar.name,
                "--cookie",
                cookie_jar.name,
                "--header",
                f"Authorization: Basic {auth}",
                "--header",
                "Accept: application/json",
                urls.geonetwork_me_url(config.catalog),
            ],
            dry_run=False,
        )
        xsrf_token = cookie_value(cookie_jar.name, "XSRF-TOKEN")
        if not xsrf_token:
            Path(cookie_jar.name).unlink(missing_ok=True)
            raise RuntimeError("Nao foi possivel obter XSRF-TOKEN do GeoNetwork.")

    try:
        metadata_upload_path, temporary_metadata = metadata_xml_with_data_dictionary_link(
            item.xml_path,
            config.data_dictionary_base_url,
            attribute_types=attribute_types,
        )
        if temporary_metadata:
            log("Link do dicionario de dados inserido no XML temporario:")
            log(f"  {config.data_dictionary_base_url}?key=<uuid>")
        else:
            log("XML importado sem alteracao temporaria do link do dicionario de dados.")

        for import_url in urls.geonetwork_records_import_urls(
            config.catalog,
            config.catalog_group,
            config.catalog_category,
        ):
            try:
                run_curl(
                    [
                        "--fail-with-body",
                        "--show-error",
                        "--location",
                        "--retry",
                        "0",
                        "--connect-timeout",
                        "60",
                        "--max-time",
                        "0",
                        "--request",
                        "POST",
                        "--cookie-jar",
                        cookie_jar.name if cookie_jar else "DRYRUN",
                        "--cookie",
                        cookie_jar.name if cookie_jar else "DRYRUN",
                        "--header",
                        f"Authorization: Basic {auth}",
                        "--header",
                        f"X-XSRF-TOKEN: {xsrf_token}",
                        "--header",
                        "Accept: application/json",
                        "--form",
                        f"file=@{metadata_upload_path};type=application/xml",
                        import_url,
                    ],
                    dry_run=dry_run,
                )
                return
            except RuntimeError as exc:
                log(f"Importacao moderna falhou em {import_url}: {exc}")

        for import_url in urls.geonetwork_legacy_import_urls(config.catalog):
            try:
                run_curl(
                    [
                        "--fail-with-body",
                        "--show-error",
                        "--retry",
                        "0",
                        "--connect-timeout",
                        "60",
                        "--max-time",
                        "0",
                        "--request",
                        "POST",
                        "--cookie-jar",
                        cookie_jar.name if cookie_jar else "DRYRUN",
                        "--cookie",
                        cookie_jar.name if cookie_jar else "DRYRUN",
                        "--header",
                        f"Authorization: Basic {auth}",
                        "--header",
                        f"X-XSRF-TOKEN: {xsrf_token}",
                        "--form",
                        f"data=<{metadata_upload_path}",
                        "--form",
                        f"group={config.catalog_group}",
                        "--form",
                        f"category={config.catalog_category}",
                        "--form",
                        "styleSheet=_none_",
                        "--form",
                        "uuidAction=overwrite",
                        "--form",
                        "isTemplate=n",
                        "--form",
                        "validate=off",
                        import_url,
                    ],
                    dry_run=dry_run,
                )
                return
            except RuntimeError as exc:
                log(f"Importacao legada falhou em {import_url}: {exc}")

        raise RuntimeError(
            f"Nao foi possivel importar metadata no GeoNetwork: {item.xml_path}"
        )
    finally:
        if metadata_upload_path != Path(item.xml_path):
            metadata_upload_path.unlink(missing_ok=True)
        if cookie_jar:
            Path(cookie_jar.name).unlink(missing_ok=True)


def cookie_value(cookie_jar, cookie_name):
    path = Path(cookie_jar)
    if not path.exists():
        return ""
    for line in reversed(path.read_text(encoding="utf-8", errors="ignore").splitlines()):
        if not line.strip() or line.lstrip().startswith("#"):
            continue
        parts = line.split("\t")
        if len(parts) >= 7 and parts[-2] == cookie_name:
            return parts[-1]
    return ""
