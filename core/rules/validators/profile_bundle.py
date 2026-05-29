from core.rules.normalization import normalize_profile_name
from core.rules.validators.common import raise_profile_errors, validate_string_list_entry
from core.rules.validators.domains import validate_domains_component, validate_fields_entry
from core.rules.validators.input_schema import (
    validate_input_schema_component,
    validate_input_schema_entry,
)
from core.rules.validators.pipeline import (
    validate_auto_functions_entry,
    validate_auto_functions_shape,
    validate_output_adjustments_entry,
    validate_pipeline_component,
    validate_postprocess_functions,
    validate_quality_outputs_entry,
)
from core.rules.validators.profile import (
    validate_profile_component,
    validate_profile_name_entry,
    validate_project_name_entry,
    validate_theme_folder_entry,
)
from core.rules.validators.relations import (
    validate_relations_component,
    validate_relations_entry,
    validate_relations_shape,
)
from core.rules.validators.style import validate_sld_entry, validate_style_component


def validate_modular_components(
    profile,
    input_schema,
    domains,
    relations,
    pipeline,
    style,
    normalized_profile_name,
):
    validate_profile_component(profile, normalized_profile_name)
    validate_input_schema_component(input_schema)
    validate_domains_component(domains)

    fields = domains.get("fields", domains)
    validate_relations_component(relations, fields)
    validate_pipeline_component(pipeline, fields)
    validate_style_component(style, fields)


def validate_rule_profile_structure(profile, profile_name):
    normalized_profile_name = normalize_profile_name(profile_name)
    if not isinstance(profile, dict):
        raise ValueError(
            f"Perfil de regras invalido '{normalized_profile_name}': "
            "o conteudo deve ser um objeto JSON."
        )

    errors = []
    validate_profile_name_entry(profile, normalized_profile_name, errors)
    validate_theme_folder_entry(profile, normalized_profile_name, errors)
    validate_project_name_entry(profile, errors)
    validate_fields_entry(profile.get("fields", {}), errors)
    validate_input_schema_entry(profile.get("input_schema", {}), errors)
    validate_relations_shape(profile.get("relations", {}), errors)
    validate_auto_functions_shape(profile.get("auto_functions", {}), errors)
    _validate_deprecated_profile_entries(profile, errors)
    validate_string_list_entry(
        profile.get("postprocess_functions", []),
        "postprocess_functions",
        errors,
    )
    validate_output_adjustments_entry(profile.get("output_adjustments", {}), errors)
    validate_quality_outputs_entry(profile.get("quality_outputs", {}), errors)
    validate_sld_entry(profile.get("sld", {}), errors, fields=profile.get("fields", {}))
    raise_profile_errors(normalized_profile_name, errors)


def validate_rule_profile_semantics(profile, profile_name, optional_functions=None):
    normalized_profile_name = normalize_profile_name(profile_name)
    errors = []
    fields = profile.get("fields", {})
    validate_relations_entry(profile.get("relations", {}), fields, errors)
    validate_auto_functions_entry(
        profile.get("auto_functions", {}),
        fields,
        errors,
        optional_functions=optional_functions,
    )
    validate_postprocess_functions(profile.get("postprocess_functions", []), errors)
    validate_output_adjustments_entry(profile.get("output_adjustments", {}), errors)
    validate_quality_outputs_entry(profile.get("quality_outputs", {}), errors)
    raise_profile_errors(normalized_profile_name, errors)


def validate_rule_profile(profile, profile_name, optional_functions=None):
    normalized_profile_name = normalize_profile_name(profile_name)
    validate_rule_profile_structure(profile, normalized_profile_name)
    validate_rule_profile_semantics(
        profile,
        normalized_profile_name,
        optional_functions=optional_functions,
    )


def _validate_deprecated_profile_entries(profile, errors):
    if "secondary_outputs" in profile:
        errors.append(
            "Campo 'secondary_outputs' foi descontinuado; configure apenas "
            "'output_adjustments' quando a saida precisar de ajuste."
        )
    if "primary_output" in profile:
        errors.append(
            "Campo 'primary_output' foi renomeado para 'output_adjustments' "
            "porque existe apenas uma saida por base."
        )

