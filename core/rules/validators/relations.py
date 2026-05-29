from core.rules.validators.common import validate_component_errors


def validate_relations_component(relations, fields):
    errors = []
    relation_entries = relations.get("relations", relations)
    validate_relations_entry(relation_entries, fields, errors)
    validate_component_errors("relations.json", errors)


def validate_relations_shape(relations, errors):
    if relations is None:
        return
    if not isinstance(relations, dict):
        errors.append("Campo 'relations' deve ser um objeto JSON.")
        return
    for relation_name, relation_mapping in relations.items():
        if not isinstance(relation_name, str) or not relation_name.strip():
            errors.append("Chaves de 'relations' devem ser strings nao vazias.")
            continue
        if not isinstance(relation_mapping, dict):
            errors.append(f"Relacao '{relation_name}' deve ser um objeto.")
            continue
        for source_value, target_value in relation_mapping.items():
            if not isinstance(source_value, str) or not isinstance(target_value, str):
                errors.append(
                    f"Relacao '{relation_name}' deve conter apenas pares string -> string."
                )
                break


def validate_relations_entry(relations, fields, errors):
    if relations is None:
        return
    if not isinstance(relations, dict):
        errors.append("Campo 'relations' deve ser um objeto JSON.")
        return

    known_fields = set(fields.keys())
    for relation_name, relation_mapping in relations.items():
        _validate_relation_entry(relation_name, relation_mapping, known_fields, errors)


def _validate_relation_entry(relation_name, relation_mapping, known_fields, errors):
    if not isinstance(relation_name, str) or not relation_name.strip():
        errors.append("Chaves de 'relations' devem ser strings nao vazias.")
        return

    if not isinstance(relation_mapping, dict):
        errors.append(f"Relacao '{relation_name}' deve ser um objeto.")
        return

    _validate_relation_fields(relation_name, known_fields, errors)

    for source_value, target_value in relation_mapping.items():
        if not isinstance(source_value, str) or not isinstance(target_value, str):
            errors.append(
                f"Relacao '{relation_name}' deve conter apenas pares string -> string."
            )
            break


def _validate_relation_fields(relation_name, known_fields, errors):
    if "_to_" not in relation_name:
        errors.append(
            f"Relacao '{relation_name}' deve seguir o padrao '<origem>_to_<destino>'."
        )
        return

    source_token, target_token = relation_name.split("_to_", 1)
    source_field = f"sdb_{source_token}"
    target_field = f"sdb_{target_token}"
    if known_fields and source_field not in known_fields and source_token not in known_fields:
        errors.append(
            f"Relacao '{relation_name}' referencia campo de origem nao configurado: "
            f"{source_field}."
        )
    if known_fields and target_field not in known_fields and target_token not in known_fields:
        errors.append(
            f"Relacao '{relation_name}' referencia campo de destino nao configurado: "
            f"{target_field}."
        )

