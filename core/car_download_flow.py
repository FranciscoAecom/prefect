from core.downloads.catalog import DOWNLOAD_TARGETS
from core.downloads.catalog import get_download_target
from core.downloads.catalog import normalize_region as normalize_uf
from core.downloads.car_api import expected_car_zip_path
from core.downloads.flow import data_download_flow


CAR_THEME_TO_DATASET_KEY = {
    target.car_theme_code: target.key
    for target in DOWNLOAD_TARGETS.values()
    if target.connector == "car_api"
}


CAR_THEMES = {
    target.car_theme_code: target
    for target in DOWNLOAD_TARGETS.values()
    if target.connector == "car_api"
}


def car_download_flow(
    theme_code="USO_RESTRITO",
    uf="MG",
    api_car_root=None,
    output_dir=None,
    extract_base=None,
    output_base=None,
    force=False,
    emit_download_event=True,
    process_after_download=True,
):
    normalized_theme_code = str(theme_code or "").strip().upper()
    try:
        dataset_key = CAR_THEME_TO_DATASET_KEY[normalized_theme_code]
    except KeyError as exc:
        valid_codes = ", ".join(sorted(CAR_THEME_TO_DATASET_KEY))
        raise ValueError(
            f"Tema CAR invalido: {theme_code}. Use: {valid_codes}"
        ) from exc
    return data_download_flow(
        dataset_key=dataset_key,
        region=uf,
        source_root=api_car_root,
        output_dir=output_dir,
        extract_base=extract_base,
        output_base=output_base,
        force=force,
        emit_download_event=emit_download_event,
        process_after_download=process_after_download,
    )


def resolve_car_theme(theme_code):
    normalized_theme_code = str(theme_code or "").strip().upper()
    try:
        return get_download_target(CAR_THEME_TO_DATASET_KEY[normalized_theme_code])
    except KeyError as exc:
        valid_codes = ", ".join(sorted(CAR_THEME_TO_DATASET_KEY))
        raise ValueError(
            f"Tema CAR invalido: {theme_code}. Use: {valid_codes}"
        ) from exc


def expected_download_zip_path(download_dir, theme, state):
    return expected_car_zip_path(download_dir, theme, state)


__all__ = [
    "CAR_THEMES",
    "car_download_flow",
    "expected_download_zip_path",
    "normalize_uf",
    "resolve_car_theme",
]
