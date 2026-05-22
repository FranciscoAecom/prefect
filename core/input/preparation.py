from core.io.dataset import read_input_dataset
from core.ingest.normalization import normalize_attribute_name
from core.rules.engine import load_rule_profile
from core.transforms.attribute_transforms import clean_whitespace, normalize_columns
from core.utils import log
from core.validation.tabular_schema import get_tabular_schema


LEGACY_COLUMN_ALIASES = {
    "sdb_des_condic": "sdb_desc_condic",
    "acm_des_condic": "acm_desc_condic",
}


def log_dataset_overview(gdf):
    from core.processing.summary import log_dataset_overview as _log_dataset_overview

    return _log_dataset_overview(gdf)


def log_queue_summary(summary, issues):
    from core.queue.summary import log_queue_summary as _log_queue_summary

    return _log_queue_summary(summary, issues)


def log_dictionary_validation(record, input_attributes):
    result = validate_rule_profile_input_schema(record, input_attributes)

    if not result["schema_found"]:
        log(
            f"Perfil sem input_schema para theme_folder '{record.theme_folder}'. "
            "Validacao estrutural nao executada."
        )
        return

    if not result["missing_attributes"] and not result["extra_attributes"]:
        log(
            f"Validacao input_schema OK para perfil '{record.rule_profile}'. "
            "Estrutura do arquivo compativel com as colunas esperadas."
        )
        return

    log(
        f"Divergencias estruturais encontradas no input_schema do perfil "
        f"'{record.rule_profile}'."
    )
    if result["missing_attributes"]:
        log(f"  Campos ausentes no arquivo: {', '.join(result['missing_attributes'])}")
    if result["extra_attributes"]:
        log(f"  Campos excedentes no arquivo: {', '.join(result['extra_attributes'])}")


def validate_rule_profile_input_schema(record, input_attributes):
    profile = load_rule_profile(record.rule_profile)
    schema = get_tabular_schema(profile)
    if schema is None:
        return {
            "schema_found": False,
            "missing_attributes": [],
            "extra_attributes": [],
        }

    input_attribute_set = {
        normalize_attribute_name(attribute)
        for attribute in input_attributes
        if is_source_schema_attribute(attribute)
    }
    expected_columns = {
        normalize_attribute_name(column)
        for column, rule in schema.columns.items()
        if rule.required and is_source_schema_attribute(column)
    }
    missing = sorted(expected_columns - input_attribute_set)
    extra = []
    if not schema.allow_extra_columns:
        allowed_columns = {
            normalize_attribute_name(column)
            for column in schema.columns
            if is_source_schema_attribute(column)
        }
        extra = sorted(input_attribute_set - allowed_columns)

    return {
        "schema_found": True,
        "missing_attributes": missing,
        "extra_attributes": extra,
    }


def is_source_schema_attribute(attribute):
    normalized = normalize_attribute_name(attribute)
    return bool(
        normalized
        and normalized != "geometry"
        and not normalized.startswith("acm_")
        and normalized != "fid"
    )


def load_and_prepare_input(record):
    gdf = read_input_dataset(record.input_path)
    gdf = normalize_columns(gdf)
    gdf = apply_legacy_column_aliases(gdf)
    log_dictionary_validation(record, list(gdf.columns))
    gdf = clean_whitespace(gdf)
    return gdf


def apply_legacy_column_aliases(gdf):
    rename_map = {
        old_column: new_column
        for old_column, new_column in LEGACY_COLUMN_ALIASES.items()
        if old_column in gdf.columns and new_column not in gdf.columns
    }
    if rename_map:
        gdf = gdf.rename(columns=rename_map)
        log(
            "Aliases legados aplicados: "
            + ", ".join(f"{old}->{new}" for old, new in sorted(rename_map.items()))
        )
    return gdf
