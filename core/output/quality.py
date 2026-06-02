from dataclasses import dataclass, field

from core.spatial.repair import INTERNAL_SAFE_REPAIR_FLAG
from core.reporting.duplicate_reports import export_duplicate_reports
from core.spatial.duplicates import (
    get_geometric_duplicate_mask,
    get_geometric_duplicate_records,
)
from core.spatial.ogc_validation import (
    get_invalid_ogc_records,
)
from core.utils import log
from core.validation.duplicates import (
    get_attribute_duplicate_mask,
    get_attribute_duplicate_records,
)
from settings import (
    ENABLE_ATTRIBUTE_DUPLICATE_REPORT,
    ENABLE_GEOMETRIC_DUPLICATE_REPORT,
    ENABLE_OGC_INVALID_REPORT,
    EXPORT_OUTPUT_QUALITY_REPORT_FILES,
)

QUALITY_CHECK_ATTRIBUTE_DUPLICATES = "check_attribute_duplicates"
QUALITY_CHECK_GEOMETRIC_DUPLICATES = "check_geometric_duplicates"
QUALITY_CHECK_OGC_INVALID_GEOMETRIES = "check_ogc_invalid_geometries"

QUALITY_OUTPUT_ATTRIBUTE_DUPLICATES = "attribute_duplicates"
QUALITY_OUTPUT_GEOMETRIC_DUPLICATES = "geometric_duplicates"
QUALITY_OUTPUT_OGC_INVALID_GEOMETRIES = "ogc_invalid_geometries"
QUALITY_OUTPUT_FULL_RECORD_DUPLICATE_FLAG = "full_record_duplicate_flag"

REPORT_LOG_SPECS = (
    ("attribute_duplicates", "duplicados atributos", "attr_report"),
    ("geometric_duplicates", "duplicados geometricos", "geom_report"),
    ("ogc_invalid_geometries", "geometrias invalidas OGC", "ogc_report"),
)

TOTAL_LOG_SPECS = (
    ("duplicados atributos", "attr_count"),
    ("duplicados geometricos", "geom_count"),
    ("geometrias invalidas OGC", "ogc_invalid_count"),
)


@dataclass(frozen=True)
class OutputQualityConfig:
    attribute_duplicates: bool = ENABLE_ATTRIBUTE_DUPLICATE_REPORT
    geometric_duplicates: bool = ENABLE_GEOMETRIC_DUPLICATE_REPORT
    ogc_invalid_geometries: bool = ENABLE_OGC_INVALID_REPORT
    export_report_files: bool = EXPORT_OUTPUT_QUALITY_REPORT_FILES
    full_record_duplicate_flag: bool = True

    @classmethod
    def from_settings(cls):
        return cls(
            attribute_duplicates=ENABLE_ATTRIBUTE_DUPLICATE_REPORT,
            geometric_duplicates=ENABLE_GEOMETRIC_DUPLICATE_REPORT,
            ogc_invalid_geometries=ENABLE_OGC_INVALID_REPORT,
            export_report_files=EXPORT_OUTPUT_QUALITY_REPORT_FILES,
            full_record_duplicate_flag=True,
        )

    @classmethod
    def from_profile(cls, rule_profile=None):
        config = cls.from_settings()
        raw_config = (rule_profile or {}).get("quality_outputs", {})
        if not isinstance(raw_config, dict):
            return config

        values = {
            "attribute_duplicates": config.attribute_duplicates,
            "geometric_duplicates": config.geometric_duplicates,
            "ogc_invalid_geometries": config.ogc_invalid_geometries,
            "export_report_files": config.export_report_files,
            "full_record_duplicate_flag": config.full_record_duplicate_flag,
        }
        key_mapping = {
            QUALITY_OUTPUT_ATTRIBUTE_DUPLICATES: "attribute_duplicates",
            QUALITY_OUTPUT_GEOMETRIC_DUPLICATES: "geometric_duplicates",
            QUALITY_OUTPUT_OGC_INVALID_GEOMETRIES: "ogc_invalid_geometries",
            QUALITY_OUTPUT_FULL_RECORD_DUPLICATE_FLAG: "full_record_duplicate_flag",
            "export_report_files": "export_report_files",
        }
        for profile_key, field_name in key_mapping.items():
            value = raw_config.get(profile_key)
            if isinstance(value, bool):
                values[field_name] = value
        return cls(**values)


@dataclass(frozen=True)
class OutputQualitySummary:
    attr_count: int
    geom_count: int
    ogc_invalid_count: int
    safe_null_count: int
    attr_report: str | None
    geom_report: str | None
    ogc_report: str | None
    ogc_error_summary: dict
    config: OutputQualityConfig = field(default_factory=OutputQualityConfig.from_settings)


def build_output_quality_summary(final_gdf, theme_output_dir, base_name, rule_profile=None):
    config = OutputQualityConfig.from_profile(rule_profile)
    attr_count, attr_duplicates = _attribute_duplicates(final_gdf, config)
    geom_count, geom_duplicates = _geometric_duplicates(final_gdf, config)
    ogc_invalid, ogc_invalid_count, ogc_error_summary = _ogc_invalid(final_gdf, config)
    attr_report, geom_report, ogc_report = _export_reports_if_needed(
        final_gdf,
        theme_output_dir,
        base_name,
        config,
        attr_count,
        attr_duplicates,
        geom_count,
        geom_duplicates,
        ogc_invalid,
        ogc_invalid_count,
        ogc_error_summary,
    )

    return OutputQualitySummary(
        attr_count=attr_count,
        geom_count=geom_count,
        ogc_invalid_count=ogc_invalid_count,
        safe_null_count=_safe_null_count(final_gdf),
        attr_report=attr_report,
        geom_report=geom_report,
        ogc_report=ogc_report,
        ogc_error_summary=ogc_error_summary,
        config=config,
    )


def log_output_quality_summary(summary):
    quality_checks = _enabled_quality_checks(summary.config)
    if quality_checks:
        log(
            "Verificacoes obrigatorias de qualidade executadas: "
            + ", ".join(quality_checks)
        )
    else:
        log("Verificacoes obrigatorias de qualidade: desabilitadas")

    for config_field, label, report_field in REPORT_LOG_SPECS:
        _log_report_status(summary, config_field, label, report_field)

    for label, count_field in TOTAL_LOG_SPECS:
        log(f"Total {label}: {getattr(summary, count_field)}")
    if summary.safe_null_count:
        log(f"Total geometrias nulas por reparo seguro: {summary.safe_null_count}")
    if summary.config.ogc_invalid_geometries and summary.ogc_error_summary:
        log("Resumo erros OGC:")
        for erro, quantidade in summary.ogc_error_summary.items():
            log(f"  {quantidade}x - {erro}")


def _log_report_status(summary, config_field, label, report_field):
    if not getattr(summary.config, config_field):
        status = "desabilitado"
    elif not summary.config.export_report_files:
        status = "exportacao de arquivo desabilitada"
    else:
        status = getattr(summary, report_field) or "nao gerado"
    log(f"Relatorio {label}: {status}")


def _enabled_quality_checks(config=None):
    config = config or OutputQualityConfig()
    checks = []
    if config.attribute_duplicates:
        checks.append(QUALITY_CHECK_ATTRIBUTE_DUPLICATES)
    if config.geometric_duplicates:
        checks.append(QUALITY_CHECK_GEOMETRIC_DUPLICATES)
    if config.ogc_invalid_geometries:
        checks.append(QUALITY_CHECK_OGC_INVALID_GEOMETRIES)
    return checks


def _attribute_duplicates(final_gdf, config):
    if not config.attribute_duplicates:
        return 0, None

    attr_dup_mask = get_attribute_duplicate_mask(final_gdf)
    attr_count = int(attr_dup_mask.sum())
    if not attr_count:
        return attr_count, None

    return attr_count, get_attribute_duplicate_records(
        final_gdf,
        dup_mask=attr_dup_mask,
    )[0]


def _geometric_duplicates(final_gdf, config):
    if not config.geometric_duplicates:
        return 0, None

    geom_dup_mask = get_geometric_duplicate_mask(final_gdf)
    geom_count = int(geom_dup_mask.sum())
    if not geom_count:
        return geom_count, None

    return geom_count, get_geometric_duplicate_records(
        final_gdf,
        dup_mask=geom_dup_mask,
    )[0]


def _ogc_invalid(final_gdf, config):
    if not config.ogc_invalid_geometries:
        return None, 0, {}
    return get_invalid_ogc_records(final_gdf)


def _export_reports_if_needed(
    final_gdf,
    theme_output_dir,
    base_name,
    config,
    attr_count,
    attr_duplicates,
    geom_count,
    geom_duplicates,
    ogc_invalid,
    ogc_invalid_count,
    ogc_error_summary,
):
    attr_report = None
    geom_report = None
    ogc_report = None

    if any(
        [
            config.attribute_duplicates and attr_count > 0,
            config.geometric_duplicates and geom_count > 0,
            config.ogc_invalid_geometries and ogc_invalid_count > 0,
        ]
    ) and config.export_report_files:
        (
            attr_report,
            geom_report,
            ogc_report,
            _,
            _,
            _,
            _,
        ) = export_duplicate_reports(
            final_gdf,
            theme_output_dir,
            base_name,
            attr_duplicates=attr_duplicates,
            attr_count=attr_count,
            geom_duplicates=geom_duplicates,
            geom_count=geom_count,
            ogc_invalid=ogc_invalid,
            ogc_invalid_count=ogc_invalid_count,
            ogc_error_summary=ogc_error_summary,
            include_full_record_duplicate_flag=config.full_record_duplicate_flag,
        )

    return attr_report, geom_report, ogc_report


def _safe_null_count(final_gdf):
    if INTERNAL_SAFE_REPAIR_FLAG not in final_gdf.columns:
        return 0
    return int(final_gdf[INTERNAL_SAFE_REPAIR_FLAG].fillna(False).sum())
