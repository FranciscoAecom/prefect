import json
import shutil
import ssl
import subprocess
import tempfile
import zipfile
from pathlib import Path
from urllib.parse import urlsplit
from urllib.parse import urlencode
from urllib.request import Request, urlopen

from core.downloads.catalog import normalize_region, resolve_theme_folder
from core.prefect_support.variables import get_path_variable, get_str_variable
from core.utils import log
from settings import DEFAULT_CAR_PUBLIC_API_BASE, DEFAULT_DOWNLOAD_ARCHIVE_BASE


def download_car_public_api_target(
    target,
    region,
    api_base=None,
    output_dir=None,
    force=False,
):
    state = normalize_region(region)
    api_base = str(
        api_base
        or get_str_variable("car_public_api_base", DEFAULT_CAR_PUBLIC_API_BASE)
    ).rstrip("/")
    archive_base = Path(output_dir) if output_dir else get_path_variable(
        "download_archive_base",
        DEFAULT_DOWNLOAD_ARCHIVE_BASE,
    )

    theme_folder = resolve_theme_folder(target, state)
    archive_dir = archive_base / target.key / theme_folder
    archive_path = archive_dir / f"{theme_folder}.zip"

    if archive_path.exists() and not force and zipfile.is_zipfile(archive_path):
        log(f"ZIP ja existe, pulando download: {archive_path}")
    else:
        if archive_path.exists() and not force:
            log(f"Arquivo existente nao e ZIP valido; baixando novamente: {archive_path}")
        archive_dir.mkdir(parents=True, exist_ok=True)
        download_url = resolve_car_download_url(api_base, state, target.car_theme_code)
        log(f"Baixando {target.display_name}/{state} em {archive_path}")
        download_file(download_url, archive_path)

    return {
        "dataset_key": target.key,
        "display_name": target.display_name,
        "connector": target.connector,
        "theme_folder": theme_folder,
        "region": state,
        "archive_path": str(archive_path),
        "zip_path": str(archive_path),
        "car_theme_code": target.car_theme_code,
        "car_theme_slug": target.car_theme_slug,
    }


def resolve_car_download_url(api_base, state, theme_code):
    query = urlencode({"uf": state, "tema": theme_code})
    endpoint = f"{api_base}/geo/zip?{query}"
    response_text = read_text_url(endpoint)
    return parse_download_url(response_text)


def read_text_url(url):
    request = Request(url, headers={"User-Agent": "data-pipeline-prefect/1.0"})
    with urlopen(request, timeout=120, context=car_ssl_context()) as response:
        return response.read().decode("utf-8")


def parse_download_url(response_text):
    text = str(response_text or "").strip()
    if not text:
        raise ValueError("API CAR retornou resposta vazia para URL de download.")

    try:
        payload = json.loads(text)
    except json.JSONDecodeError:
        return text.strip('"')

    if isinstance(payload, str):
        return payload
    if isinstance(payload, dict):
        for key in ("url", "downloadUrl", "download_url", "href"):
            value = payload.get(key)
            if value:
                return str(value)
    raise ValueError(f"Resposta da API CAR sem URL reconhecida: {payload!r}")


def download_file(url, destination):
    destination = Path(destination)
    destination.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile(
        delete=False,
        dir=destination.parent,
        suffix=".part",
    ) as temp_file:
        temp_path = Path(temp_file.name)
        temp_file.close()
        if shutil.which("curl.exe"):
            download_file_with_curl(url, temp_path)
        else:
            request = Request(url, headers={"User-Agent": "data-pipeline-prefect/1.0"})
            with urlopen(request, timeout=3600, context=car_ssl_context()) as response:
                with temp_path.open("wb") as output:
                    shutil.copyfileobj(response, output)

    try:
        validate_zip_download(temp_path, url)
        temp_path.replace(destination)
    except Exception:
        temp_path.unlink(missing_ok=True)
        raise


def download_file_with_curl(url, destination):
    arguments = [
        "curl.exe",
        "--insecure",
        "--ssl-no-revoke",
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
        "--output",
        str(destination),
        url,
    ]
    result = subprocess.run(
        arguments,
        capture_output=True,
        text=True,
        check=False,
    )
    if result.returncode != 0:
        output = "\n".join(
            part.strip()
            for part in (result.stdout, result.stderr)
            if part and part.strip()
        )
        raise RuntimeError(f"curl.exe falhou ao baixar arquivo CAR: {output}")


def validate_zip_download(path, url):
    if zipfile.is_zipfile(path):
        return
    sample = path.read_text(encoding="utf-8", errors="replace")[:500].strip()
    message = "Download CAR nao retornou um ZIP valido."
    if sample:
        message = f"{message} Inicio da resposta: {sample}"
    raise ValueError(f"{message} URL sem assinatura: {redact_signed_url(url)}")


def redact_signed_url(url):
    parsed = urlsplit(str(url))
    return f"{parsed.scheme}://{parsed.netloc}{parsed.path}"


def car_ssl_context():
    # A API publica do CAR pode entregar cadeia com certificado corporativo/autoassinado.
    return ssl._create_unverified_context()


__all__ = [
    "download_car_public_api_target",
    "download_file",
    "download_file_with_curl",
    "parse_download_url",
    "car_ssl_context",
    "redact_signed_url",
    "resolve_car_download_url",
    "validate_zip_download",
]
