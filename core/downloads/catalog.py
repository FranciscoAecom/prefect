from dataclasses import dataclass


@dataclass(frozen=True)
class DownloadTarget:
    key: str
    display_name: str
    connector: str
    theme_folder_prefix: str
    car_theme_code: str | None = None
    car_theme_slug: str | None = None
    requires_region: bool = True
    default_region: str | None = None


DOWNLOAD_TARGETS = {
    "car_app": DownloadTarget(
        key="car_app",
        display_name="CAR - Area de Preservacao Permanente",
        connector="car_api",
        theme_folder_prefix="app_car",
        car_theme_code="APPS",
        car_theme_slug="area_preservacao_permanente",
    ),
    "car_reserva_legal": DownloadTarget(
        key="car_reserva_legal",
        display_name="CAR - Reserva Legal",
        connector="car_api",
        theme_folder_prefix="rl_car",
        car_theme_code="RESERVA_LEGAL",
        car_theme_slug="reserva_legal",
    ),
    "car_servidao_administrativa": DownloadTarget(
        key="car_servidao_administrativa",
        display_name="CAR - Servidao Administrativa",
        connector="car_api",
        theme_folder_prefix="sa_car",
        car_theme_code="SERVIDAO_ADMINISTRATIVA",
        car_theme_slug="servidao_administrativa",
    ),
    "car_uso_restrito": DownloadTarget(
        key="car_uso_restrito",
        display_name="CAR - Uso Restrito",
        connector="car_api",
        theme_folder_prefix="ur_car",
        car_theme_code="USO_RESTRITO",
        car_theme_slug="uso_restrito",
    ),
}


def get_download_target(dataset_key):
    normalized = str(dataset_key or "").strip().lower()
    try:
        return DOWNLOAD_TARGETS[normalized]
    except KeyError as exc:
        valid_keys = ", ".join(sorted(DOWNLOAD_TARGETS))
        raise ValueError(f"Dataset de download invalido: {dataset_key}. Use: {valid_keys}") from exc


def normalize_region(region):
    normalized = str(region or "").strip().upper()
    if len(normalized) != 2:
        raise ValueError(f"Regiao/UF invalida: {region}")
    return normalized


def resolve_theme_folder(target, region):
    if target.requires_region:
        return f"{target.theme_folder_prefix}_{normalize_region(region).lower()}"
    return target.theme_folder_prefix


__all__ = [
    "DOWNLOAD_TARGETS",
    "DownloadTarget",
    "get_download_target",
    "normalize_region",
    "resolve_theme_folder",
]
