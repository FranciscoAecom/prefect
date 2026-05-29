def validate_component_errors(component_name, errors):
    if errors:
        message = "\n".join(f"- {error}" for error in errors)
        raise ValueError(f"Componente '{component_name}' invalido:\n{message}")


def validate_string_list_entry(values, field_name, errors):
    if values is None:
        return
    if not isinstance(values, list):
        errors.append(f"Campo '{field_name}' deve ser uma lista.")
        return
    for value in values:
        if not isinstance(value, str) or not value.strip():
            errors.append(f"Campo '{field_name}' deve conter apenas strings nao vazias.")
            break


def validate_registered_function_list(values, field_name, registered_names, errors):
    if values is None:
        return
    if not isinstance(values, list):
        return
    for value in values:
        if not isinstance(value, str) or not value.strip():
            continue
        if value not in registered_names and resolve_qualified_function(value) is None:
            errors.append(f"Funcao '{value}' em '{field_name}' nao esta registrada.")


def resolve_qualified_function(func_name):
    from core.configured_steps import resolve_qualified_function as resolve

    return resolve(func_name)


def get_registered_postprocess_function_names():
    from core.configured_steps import get_registered_postprocess_function_names

    return get_registered_postprocess_function_names()


def raise_profile_errors(normalized_profile_name, errors):
    if errors:
        message = "\n".join(f"- {error}" for error in errors)
        raise ValueError(
            f"Perfil de regras invalido '{normalized_profile_name}':\n{message}"
        )

