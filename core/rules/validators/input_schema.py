from core.rules.validators.common import validate_component_errors


def validate_input_schema_component(input_schema):
    errors = []

    if not input_schema:
        return

    columns = input_schema.get("columns", {})
    if not isinstance(columns, dict):
        errors.append("Campo 'columns' deve ser um objeto JSON.")
        columns = {}

    for column, rule in columns.items():
        _validate_column_rule(column, rule, errors)

    for key in ("require_geometry", "allow_extra_columns"):
        value = input_schema.get(key, True)
        if not isinstance(value, bool):
            errors.append(f"Campo '{key}' deve ser booleano.")

    validate_component_errors("input_schema.json", errors)


def validate_input_schema_entry(input_schema, errors):
    if not input_schema:
        return
    try:
        validate_input_schema_component(input_schema)
    except ValueError as exc:
        errors.append(str(exc))


def _validate_column_rule(column, rule, errors):
    if not isinstance(column, str) or not column.strip():
        errors.append("Chaves de 'columns' devem ser strings nao vazias.")
        return

    if isinstance(rule, str):
        if not rule.strip():
            errors.append(f"Tipo de '{column}' deve ser uma string nao vazia.")
        return

    if not isinstance(rule, dict):
        errors.append(f"Regra de coluna '{column}' deve ser string ou objeto JSON.")
        return

    dtype = rule.get("dtype", "string")
    if not isinstance(dtype, str) or not dtype.strip():
        errors.append(f"'dtype' de '{column}' deve ser uma string nao vazia.")

    for key in ("required", "nullable"):
        value = rule.get(key, True)
        if not isinstance(value, bool):
            errors.append(f"'{key}' de '{column}' deve ser booleano.")

