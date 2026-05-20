import subprocess
from pathlib import Path

from core.downloads.catalog import normalize_region, resolve_theme_folder
from core.prefect_support.variables import get_path_variable
from core.utils import log
from settings import DEFAULT_API_CAR_ROOT


def download_car_api_target(
    target,
    region,
    api_car_root=None,
    output_dir=None,
    force=False,
):
    state = normalize_region(region)
    api_root = Path(api_car_root) if api_car_root else get_path_variable(
        "api_car_root",
        DEFAULT_API_CAR_ROOT,
    )
    script_path = api_root / "scripts" / "download_tema_car.ps1"

    if not script_path.exists():
        raise FileNotFoundError(f"Script de download nao encontrado: {script_path}")

    download_dir = (
        Path(output_dir)
        if output_dir
        else api_root / "downloads" / target.car_theme_slug
    )
    command = [
        "powershell",
        "-ExecutionPolicy",
        "Bypass",
        "-File",
        str(script_path),
        "-ThemeCode",
        target.car_theme_code,
        "-ThemeSlug",
        target.car_theme_slug,
        "-OutputDir",
        str(download_dir),
        "-Uf",
        state,
        "-LowercaseFileName",
    ]
    if force:
        command.append("-Force")

    log(f"Baixando {target.display_name}/{state} em {download_dir}")
    completed = subprocess.run(
        command,
        cwd=str(api_root),
        capture_output=True,
        text=True,
        check=False,
    )
    if completed.stdout:
        print(completed.stdout)
    if completed.stderr:
        print(completed.stderr)
    if completed.returncode != 0:
        raise RuntimeError(
            f"Download falhou para {target.key}/{state}: {completed.returncode}"
        )

    zip_path = expected_car_zip_path(download_dir, target, state)
    if not zip_path.exists():
        raise FileNotFoundError(f"ZIP baixado nao encontrado: {zip_path}")

    theme_folder = resolve_theme_folder(target, state)
    return {
        "dataset_key": target.key,
        "display_name": target.display_name,
        "connector": target.connector,
        "theme_folder": theme_folder,
        "region": state,
        "archive_path": str(zip_path),
        "zip_path": str(zip_path),
        "car_theme_code": target.car_theme_code,
        "car_theme_slug": target.car_theme_slug,
    }


def expected_car_zip_path(download_dir, target, state):
    folder_name = f"car_{target.car_theme_slug}_{state.lower()}"
    file_name = f"{folder_name}.zip"
    return Path(download_dir) / folder_name / file_name


__all__ = ["download_car_api_target", "expected_car_zip_path"]
