import json
from pathlib import Path
from urllib.parse import urlencode

from core.downloads.archive import is_valid_zip, validate_zip_download
from core.downloads.catalog import normalize_region, resolve_theme_folder
from core.downloads.http import download_url, read_text_url
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

    if archive_path.exists() and not force and is_valid_zip(archive_path):
        log(f"ZIP ja existe, pulando download: {archive_path}")
    else:
        if archive_path.exists() and not force:
            log(f"Arquivo existente nao e ZIP valido; baixando novamente: {archive_path}")
        archive_dir.mkdir(parents=True, exist_ok=True)
        download_url = resolve_car_download_url(api_base, state, target.car_theme_code)
        log(f"Baixando {target.display_name}/{state} em {archive_path}")
        download_car_zip(download_url, archive_path)

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

def download_car_zip(url, destination):
    download_url(url, destination, validator=validate_zip_download)


__all__ = [
    "download_car_public_api_target",
    "download_car_zip",
    "parse_download_url",
    "resolve_car_download_url",
]
