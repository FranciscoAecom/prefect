from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[2]


DEFAULT_CAR_PUBLIC_API_BASE = "https://consulta.car.gov.br/api"
DEFAULT_DOWNLOAD_EXTRACT_BASE = PROJECT_ROOT / "input" / "downloads"
DEFAULT_DOWNLOAD_ARCHIVE_BASE = DEFAULT_DOWNLOAD_EXTRACT_BASE / "_archives"
DEFAULT_MUNICIPALITIES_BASE_PATH = (
    r"L:\Secure_DCS\BRBLH1PINFW001\COE_Digital\coe_digital_data\silver_data"
    r"\restricted\loc\municipios\IBGE\20240101\00\pol_loc_mun_20230101.gpkg"
)
DEFAULT_BRAZIL_BBOX_PATH = (
    r"L:\Secure_DCS\BRBLH1PINFW001\COE_Digital\others\bouding_box"
    r"\brasil\pol_br_zona_costeira.gpkg"
)


__all__ = [
    "DEFAULT_BRAZIL_BBOX_PATH",
    "DEFAULT_CAR_PUBLIC_API_BASE",
    "DEFAULT_DOWNLOAD_ARCHIVE_BASE",
    "DEFAULT_DOWNLOAD_EXTRACT_BASE",
    "DEFAULT_MUNICIPALITIES_BASE_PATH",
]
