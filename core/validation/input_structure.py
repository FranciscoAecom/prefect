from core.ingest.normalization import normalize_attribute_name
from core.rules.engine import load_rule_profile
from core.validation.tabular_schema import get_tabular_schema


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


__all__ = ["is_source_schema_attribute", "validate_rule_profile_input_schema"]
