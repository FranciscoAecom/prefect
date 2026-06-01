from core.rules.domain_hygiene import looks_like_mojibake
from core.rules.validators.common import validate_component_errors


def validate_domains_component(domains):
    errors = []
    fields = domains.get("fields", domains)
    validate_fields_entry(fields, errors)
    validate_component_errors("domains.json", errors)


def validate_fields_entry(fields, errors):
    if fields is None:
        return {}
    if not isinstance(fields, dict):
        errors.append("Campo 'fields' deve ser um objeto JSON.")
        return {}

    for field_name, field_rules in fields.items():
        _validate_field_rules(field_name, field_rules, errors)

    return fields


def _validate_field_rules(field_name, field_rules, errors):
    if not isinstance(field_name, str) or not field_name.strip():
        errors.append("Chaves de 'fields' devem ser strings nao vazias.")
        return

    if not isinstance(field_rules, dict):
        errors.append(f"Configuracao de field '{field_name}' deve ser um objeto.")
        return

    accepted_values = field_rules.get("accepted_values", [])
    aliases = field_rules.get("aliases", {})

    if accepted_values is None:
        accepted_values = []
    if not isinstance(accepted_values, list):
        errors.append(f"'accepted_values' de '{field_name}' deve ser uma lista.")
        accepted_values = []

    if not all(isinstance(value, str) for value in accepted_values):
        errors.append(
            f"'accepted_values' de '{field_name}' deve conter apenas strings."
        )
    elif any(looks_like_mojibake(value) for value in accepted_values):
        errors.append(
            f"'accepted_values' de '{field_name}' nao deve conter texto com possivel mojibake."
        )

    if aliases is None:
        aliases = {}
    if not isinstance(aliases, dict):
        errors.append(f"'aliases' de '{field_name}' deve ser um objeto.")
        aliases = {}

    if not all(isinstance(key, str) for key in aliases.keys()):
        errors.append(f"'aliases' de '{field_name}' deve usar chaves string.")
    if not all(isinstance(value, str) for value in aliases.values()):
        errors.append(f"'aliases' de '{field_name}' deve usar valores string.")
    elif any(looks_like_mojibake(value) for value in aliases.values()):
        errors.append(
            f"Destinos de 'aliases' de '{field_name}' nao devem conter texto com possivel mojibake."
        )

    _validate_alias_targets(field_name, accepted_values, aliases, errors)


def _validate_alias_targets(field_name, accepted_values, aliases, errors):
    accepted_values_set = set(accepted_values)
    for alias, canonical in aliases.items():
        if not isinstance(alias, str) or not isinstance(canonical, str):
            continue
        if canonical not in accepted_values_set:
            errors.append(
                f"Alias '{alias}' de '{field_name}' aponta para valor fora de "
                f"'accepted_values': {canonical}."
            )
