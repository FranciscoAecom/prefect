from dataclasses import dataclass
from datetime import datetime
from pathlib import Path

import pandas as pd

from core.ingest.normalization import normalize_theme_folder, stringify
from core.ingest.status_flags import parse_ingest_status
from settings import (
    DATA_LAKE_BASE,
    DATA_LAKE_BRONZE_STAGE,
    DATA_LAKE_SILVER_STAGE,
    DATA_LAKE_TEMP_STAGE,
)


GEOGRAPHIC_SUFFIXES = {".gpkg", ".shp", ".tif", ".tiff"}
VERSION_START = "00"
VERSION_WIDTH = 2


@dataclass(frozen=True)
class DatasetVersionPlan:
    base_path: Path
    access_constraints: str
    category_acronym: str
    theme_folder: str
    citation: str
    date_folder: str
    version: str
    status: str
    temp_dir: Path
    bronze_dir: Path
    silver_dir: Path


def resolve_dataset_version_plan(record, base_path=DATA_LAKE_BASE, create=True):
    status = _field(record, "status")
    date_folder = normalize_date_folder(_field(record, "date"))

    common_parts = {
        "base_path": Path(base_path),
        "access_constraints": _required_path_part(record, "access_constraints"),
        "category_acronym": _required_path_part(record, "category_acronym"),
        "theme_folder": _required_path_part(record, "theme_folder", normalize_theme_folder),
        "citation": _required_path_part(record, "citation"),
        "date_folder": date_folder,
        "status": status,
    }

    bronze_date_root = build_stage_root(
        stage=DATA_LAKE_BRONZE_STAGE,
        version=None,
        **common_parts,
    )
    version = resolve_next_available_version(
        bronze_date_root,
        status=status,
    )

    plan = DatasetVersionPlan(
        version=version,
        temp_dir=build_stage_root(stage=DATA_LAKE_TEMP_STAGE, version=version, **common_parts),
        bronze_dir=build_stage_root(
            stage=DATA_LAKE_BRONZE_STAGE,
            version=version,
            **common_parts,
        ),
        silver_dir=build_stage_root(
            stage=DATA_LAKE_SILVER_STAGE,
            version=version,
            **common_parts,
        ),
        **common_parts,
    )

    if create:
        plan.temp_dir.mkdir(parents=True, exist_ok=True)
        plan.bronze_dir.mkdir(parents=True, exist_ok=True)
        plan.silver_dir.mkdir(parents=True, exist_ok=True)

    return plan


def build_stage_root(
    base_path,
    stage,
    access_constraints,
    category_acronym,
    theme_folder,
    citation,
    date_folder,
    status=None,
    version=None,
):
    parts = [
        Path(base_path),
        _safe_path_part(stage, "stage"),
        _safe_path_part(access_constraints, "access_constraints"),
        _safe_path_part(category_acronym, "category_acronym"),
        _safe_path_part(theme_folder, "theme_folder"),
        _safe_path_part(citation, "citation"),
        normalize_date_folder(date_folder),
    ]
    if version is not None:
        parts.append(normalize_version_folder(version))
    path = parts[0]
    for part in parts[1:]:
        path = path / part
    return path


def resolve_next_available_version(date_root, status):
    date_root = Path(date_root)
    ingest_status = parse_ingest_status(status)
    if not (ingest_status.has_treatment or ingest_status.has_download):
        raise ValueError(
            "Status sem regra de versionamento: "
            f"{status}. Use download, treatment ou download-treatment."
        )

    version_number = int(VERSION_START)
    while True:
        candidate = normalize_version_folder(version_number)
        candidate_dir = date_root / candidate
        if not contains_geographic_dataset(candidate_dir):
            return candidate
        version_number += 1


def contains_geographic_dataset(path):
    path = Path(path)
    if not path.exists():
        return False
    return any(
        candidate.is_file() and candidate.suffix.lower() in GEOGRAPHIC_SUFFIXES
        for candidate in path.rglob("*")
    )


def normalize_date_folder(value):
    text = stringify(value)
    if not text:
        raise ValueError("Campo date vazio para versionamento.")
    if text.isdigit() and len(text) == 8:
        return text

    parsed = _parse_date(value)
    if parsed is None:
        raise ValueError(f"Campo date invalido para versionamento: {value}")
    return parsed.strftime("%Y%m%d")


def normalize_version_folder(value):
    text = stringify(value) or VERSION_START
    if text.endswith(".0") and text[:-2].isdigit():
        text = text[:-2]
    if not text.isdigit():
        raise ValueError(f"Versao invalida: {value}")
    return str(int(text)).zfill(VERSION_WIDTH)


def _parse_date(value):
    if isinstance(value, datetime):
        return value
    if hasattr(value, "to_pydatetime"):
        return value.to_pydatetime()

    text = stringify(value)
    for dayfirst in (False, True):
        parsed = pd.to_datetime(text, errors="coerce", dayfirst=dayfirst)
        if not pd.isna(parsed):
            return parsed.to_pydatetime()
    return None


def _field(record, field_name, default=""):
    if isinstance(record, dict):
        return record.get(field_name, default)
    return getattr(record, field_name, default)


def _required_path_part(record, field_name, normalizer=stringify):
    value = normalizer(_field(record, field_name))
    return _safe_path_part(value, field_name)


def _safe_path_part(value, field_name):
    text = stringify(value)
    if not text:
        raise ValueError(f"Campo {field_name} vazio para montagem do caminho.")
    if any(separator in text for separator in ("/", "\\")):
        raise ValueError(f"Campo {field_name} contem separador de caminho: {text}")
    if any(char in text for char in '<>:"|?*'):
        raise ValueError(f"Campo {field_name} contem caractere invalido: {text}")
    return text
