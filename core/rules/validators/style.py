from core.rules.validators.common import validate_component_errors


def validate_style_component(style, fields=None):
    errors = []
    validate_sld_entry((style or {}).get("sld", style or {}), errors, fields=fields)
    validate_component_errors("style.json", errors)


def validate_sld_entry(sld, errors, fields=None):
    if sld in (None, {}):
        return
    if not isinstance(sld, dict):
        errors.append("Campo 'sld' deve ser um objeto JSON.")
        return

    if "rule_name" in sld and not isinstance(sld["rule_name"], str):
        errors.append("Campo 'sld.rule_name' deve ser string.")

    for section in ("point", "line", "polygon"):
        _validate_style_section(sld, section, errors)

    validate_sld_rules_against_domains(sld, fields or {}, errors)


def validate_sld_rules_against_domains(sld, fields, errors):
    if not isinstance(fields, dict):
        return

    rules_by_property = {}
    for rule in iter_sld_rules(sld):
        rule_filter = rule.get("filter", {}) if isinstance(rule, dict) else {}
        if not isinstance(rule_filter, dict):
            continue
        property_name = rule_filter.get("property")
        literal = rule_filter.get("literal")
        if not property_name or literal is None:
            continue
        rules_by_property.setdefault(str(property_name), set()).add(str(literal))

    for property_name, literals in sorted(rules_by_property.items()):
        _validate_sld_property_literals(property_name, literals, fields, errors)


def iter_sld_rules(sld):
    rules = sld.get("rules", [])
    if isinstance(rules, list):
        yield from (rule for rule in rules if isinstance(rule, dict))

    layers = sld.get("layers", {})
    if not isinstance(layers, dict):
        return
    for layer_style in layers.values():
        if not isinstance(layer_style, dict):
            continue
        layer_rules = layer_style.get("rules", [])
        if isinstance(layer_rules, list):
            yield from (rule for rule in layer_rules if isinstance(rule, dict))


def _validate_style_section(sld, section, errors):
    value = sld.get(section)
    if value is None:
        return
    if not isinstance(value, dict):
        errors.append(f"Campo 'sld.{section}' deve ser um objeto JSON.")
        return
    for key, style_value in value.items():
        if not isinstance(key, str) or not key.strip():
            errors.append(f"Chaves de 'sld.{section}' devem ser strings nao vazias.")
            continue
        if style_value is not None and not isinstance(style_value, (str, int, float)):
            errors.append(
                f"Valor de 'sld.{section}.{key}' deve ser string ou numero."
            )


def _validate_sld_property_literals(property_name, literals, fields, errors):
    field_rules = fields.get(property_name)
    if not isinstance(field_rules, dict):
        return
    accepted_values = field_rules.get("accepted_values", [])
    if not accepted_values:
        return
    accepted_values = {str(value) for value in accepted_values}
    unknown_literals = sorted(literals - accepted_values)
    missing_literals = sorted(accepted_values - literals)
    if unknown_literals:
        errors.append(
            "SLD referencia valor fora do dominio em "
            f"'{property_name}': {', '.join(unknown_literals)}."
        )
    if missing_literals:
        errors.append(
            "SLD nao cobre todos os valores aceitos de "
            f"'{property_name}': {', '.join(missing_literals)}."
        )

