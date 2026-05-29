from core.rules.contracts import OUTPUT_ADJUSTMENT_OPTIONS, PIPELINE_COMPONENT_KEYS
from core.rules.validators.common import (
    get_registered_postprocess_function_names,
    resolve_qualified_function,
    validate_component_errors,
    validate_registered_function_list,
    validate_string_list_entry,
)


QUALITY_OUTPUT_OPTIONS = {
    "attribute_duplicates",
    "geometric_duplicates",
    "ogc_invalid_geometries",
    "export_report_files",
    "full_record_duplicate_flag",
}


def validate_pipeline_component(pipeline, fields):
    errors = []
    _validate_deprecated_pipeline_entries(pipeline, errors)
    auto_functions = (
        pipeline.get("auto_functions", {})
        if pipeline_uses_component_keys(pipeline)
        else pipeline
    )
    validate_auto_functions_entry(auto_functions, fields, errors)
    validate_string_list_entry(
        pipeline.get("postprocess_functions", []),
        "postprocess_functions",
        errors,
    )
    validate_output_adjustments_entry(pipeline.get("output_adjustments", {}), errors)
    validate_quality_outputs_entry(pipeline.get("quality_outputs", {}), errors)
    validate_component_errors("pipeline.json", errors)


def pipeline_uses_component_keys(pipeline):
    return any(key in pipeline for key in PIPELINE_COMPONENT_KEYS)


def validate_auto_functions_shape(auto_functions, errors):
    if auto_functions is None:
        return
    if not isinstance(auto_functions, dict):
        errors.append("Campo 'auto_functions' deve ser um objeto JSON.")
        return
    for column, functions in auto_functions.items():
        if not isinstance(column, str) or not column.strip():
            errors.append("Chaves de 'auto_functions' devem ser strings nao vazias.")
            continue
        if not isinstance(functions, list) or not functions:
            errors.append(
                f"'auto_functions.{column}' deve ser uma lista nao vazia de funcoes."
            )
            continue
        for func_name in functions:
            if not isinstance(func_name, str) or not func_name.strip():
                errors.append(
                    f"'auto_functions.{column}' deve conter apenas nomes de funcao string."
                )


def validate_output_adjustments_entry(output_adjustments, errors):
    if output_adjustments in (None, {}):
        return
    if not isinstance(output_adjustments, dict):
        errors.append("Campo 'output_adjustments' deve ser um objeto JSON.")
        return

    for key, value in output_adjustments.items():
        if key not in OUTPUT_ADJUSTMENT_OPTIONS:
            errors.append(f"Opcao desconhecida em 'output_adjustments': {key}.")
            continue
        if not isinstance(value, bool):
            errors.append(f"Campo 'output_adjustments.{key}' deve ser booleano.")


def validate_quality_outputs_entry(quality_outputs, errors):
    if quality_outputs in (None, {}):
        return
    if not isinstance(quality_outputs, dict):
        errors.append("Campo 'quality_outputs' deve ser um objeto JSON.")
        return

    for key, value in quality_outputs.items():
        if key not in QUALITY_OUTPUT_OPTIONS:
            errors.append(f"Opcao desconhecida em 'quality_outputs': {key}.")
            continue
        if not isinstance(value, bool):
            errors.append(f"Campo 'quality_outputs.{key}' deve ser booleano.")


def validate_auto_functions_entry(
    auto_functions,
    fields,
    errors,
    optional_functions=None,
):
    if auto_functions is None:
        return
    if not isinstance(auto_functions, dict):
        errors.append("Campo 'auto_functions' deve ser um objeto JSON.")
        return

    known_fields = set(fields.keys())
    for column, functions in auto_functions.items():
        _validate_auto_function_column(
            column,
            functions,
            known_fields,
            errors,
            optional_functions=optional_functions,
        )


def validate_postprocess_functions(values, errors):
    validate_registered_function_list(
        values,
        "postprocess_functions",
        get_registered_postprocess_function_names(),
        errors,
    )


def _validate_deprecated_pipeline_entries(pipeline, errors):
    if "sld" in pipeline:
        errors.append("Campo 'sld' deve ficar em style.json, nao em pipeline.json.")
    if "secondary_outputs" in pipeline:
        errors.append(
            "Campo 'secondary_outputs' foi descontinuado; configure apenas "
            "'output_adjustments' quando a saida precisar de ajuste."
        )
    if "primary_output" in pipeline:
        errors.append(
            "Campo 'primary_output' foi renomeado para 'output_adjustments' "
            "porque existe apenas uma saida por base."
        )


def _validate_auto_function_column(
    column,
    functions,
    known_fields,
    errors,
    optional_functions=None,
):
    if not isinstance(column, str) or not column.strip():
        errors.append("Chaves de 'auto_functions' devem ser strings nao vazias.")
        return

    if not isinstance(functions, list) or not functions:
        errors.append(
            f"'auto_functions.{column}' deve ser uma lista nao vazia de funcoes."
        )
        return

    for func_name in functions:
        _validate_auto_function_name(
            column,
            func_name,
            known_fields,
            errors,
            optional_functions=optional_functions,
        )


def _validate_auto_function_name(
    column,
    func_name,
    known_fields,
    errors,
    optional_functions=None,
):
    if not isinstance(func_name, str) or not func_name.strip():
        errors.append(
            f"'auto_functions.{column}' deve conter apenas nomes de funcao string."
        )
        return

    if (
        optional_functions is not None
        and func_name not in optional_functions
        and resolve_qualified_function(func_name) is None
    ):
        errors.append(
            f"Funcao '{func_name}' em 'auto_functions.{column}' nao esta registrada."
        )
        return

    if (
        func_name == "validate_shapefile_attribute"
        and known_fields
        and column not in known_fields
    ):
        errors.append(
            f"Campo '{column}' usa 'validate_shapefile_attribute' mas nao possui "
            "configuracao correspondente em 'fields'."
        )

