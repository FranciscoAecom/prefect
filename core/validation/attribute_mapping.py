import unicodedata
from difflib import get_close_matches

from core.rules.engine import build_field_mapping, has_field_rules
from core.utils import log
from core.validation.session import validation_session_or_default
from settings import INTERACTIVE_ATTRIBUTE_REVIEW


def normalize_for_compare(value):
    if not isinstance(value, str):
        return ""
    text = value.strip()
    text = unicodedata.normalize("NFKD", text)
    text = "".join(ch for ch in text if ord(ch) < 128)
    return text.upper()


def get_non_empty_unique_text_values(series):
    values = series.dropna().astype(str).str.strip()
    values = values[values != ""]
    return values.drop_duplicates().tolist()


def build_fuzzy_mapping(gdf, column):
    unique_values = get_non_empty_unique_text_values(gdf[column])
    if not unique_values:
        return {}

    canonical_norms = []
    canonical_values = []
    replacements = {}

    for value in unique_values:
        normalized = normalize_for_compare(value)

        if not normalized:
            replacements[value] = value
            continue

        close = get_close_matches(normalized, canonical_norms, n=1, cutoff=0.9)
        if close:
            replacements[value] = canonical_values[canonical_norms.index(close[0])]
            continue

        canonical_norms.append(normalized)
        canonical_values.append(value)
        replacements[value] = value

    return replacements


def build_validate_attribute_mapping(gdf, column, rule_profile):
    unique_values = get_non_empty_unique_text_values(gdf[column])

    if not unique_values:
        return {
            "replacements": {},
            "corrections": [],
            "invalid_values": [],
            "strategy": "empty",
        }

    if has_field_rules(rule_profile, column):
        replacements, corrections, invalid_values = build_field_mapping(
            rule_profile,
            column,
            unique_values,
        )
        return {
            "replacements": replacements,
            "corrections": corrections,
            "invalid_values": invalid_values,
            "strategy": "domain_rules",
        }

    replacements = build_fuzzy_mapping(gdf, column)
    corrections = [(value, target) for value, target in replacements.items() if value != target]
    return {
        "replacements": replacements,
        "corrections": corrections,
        "invalid_values": [],
        "strategy": "fuzzy",
    }


def has_optional_function(funcs, function_name):
    return any(
        str(func) == function_name or str(func).endswith(f".{function_name}")
        for func in funcs
    )


def prepare_validate_shapefile_attribute_mappings(
    gdf,
    mapping,
    rule_profile,
    validation_session=None,
    input_func=input,
):
    validation_session = validation_session_or_default(validation_session)
    for column, funcs in mapping.items():
        if not has_optional_function(funcs, "validate_shapefile_attribute"):
            continue

        if column not in gdf.columns:
            log(f"Atributo {column} nao encontrado para validacao")
            continue

        if column in validation_session.attribute_mappings:
            continue

        mapping_result = build_validate_attribute_mapping(gdf, column, rule_profile)
        replacements = mapping_result["replacements"]
        corrections = mapping_result["corrections"]
        strategy = mapping_result["strategy"]

        if not replacements:
            log(f"Nenhum valor unico encontrado em {column} para validacao")
            validation_session.attribute_mappings[column] = {}
            continue

        if strategy == "domain_rules":
            validation_session.attribute_mappings[column] = replacements
            continue

        validation_session.attribute_mappings[column] = _resolve_fuzzy_attribute_mapping(
            column,
            replacements,
            corrections,
            input_func=input_func,
        )


def _resolve_fuzzy_attribute_mapping(
    column,
    replacements,
    corrections,
    input_func=input,
):
    log(f"\nSugestoes de correcao De:Para para {column}:", raw=True)

    if not corrections:
        log("  Nenhuma sugestao de correcao encontrada.", raw=True)
        return {}

    displayed_suggestions = _display_correction_suggestions(corrections)

    log("", raw=True)
    if not INTERACTIVE_ATTRIBUTE_REVIEW:
        log(
            "Modo nao interativo habilitado em settings.py; "
            "nenhuma sugestao fuzzy sera aplicada automaticamente.",
            raw=True,
        )
        return {}

    selected_suggestions = _prompt_selected_suggestions(
        column,
        displayed_suggestions,
        input_func=input_func,
    )
    if not selected_suggestions:
        return {}

    selected_replacements = _build_selected_replacements(
        replacements,
        selected_suggestions,
    )
    log(
        f"{len(selected_suggestions)} correcao(oes) aplicada(s) para {column}.",
        raw=True,
    )
    return selected_replacements


def _display_correction_suggestions(corrections, max_display=100):
    displayed_suggestions = corrections[:max_display]
    for idx, (value, target) in enumerate(displayed_suggestions, 1):
        log(f" {idx}. {value:80} -> {target}", raw=True)

    if len(corrections) > max_display:
        log(f"  ... e mais {len(corrections) - max_display} correcoes", raw=True)

    return displayed_suggestions


def _prompt_selected_suggestions(column, displayed_suggestions, input_func=input):
    log("Informe os numeros das correcoes que deseja aplicar.", raw=True)
    log("Exemplos: 1,3,4 | all | ENTER para nao aplicar nenhuma", raw=True)

    choice = input_func(f"Aplicar quais correcoes para a coluna '{column}'? ")
    normalized_choice = choice.strip().lower()

    if not normalized_choice:
        log(f"Nenhuma correcao aplicada para {column}.", raw=True)
        return []

    if normalized_choice == "all":
        return displayed_suggestions

    try:
        selected_indices = {
            int(item.strip()) for item in choice.split(",") if item.strip()
        }
    except ValueError:
        log(f"Entrada invalida para {column}. Nenhuma correcao aplicada.", raw=True)
        return []

    invalid_indices = [
        idx for idx in selected_indices if idx < 1 or idx > len(displayed_suggestions)
    ]
    if invalid_indices:
        invalid_display = ", ".join(str(i) for i in sorted(invalid_indices))
        log(
            f"Indices invalidos para {column}: {invalid_display}. "
            "Nenhuma correcao aplicada.",
            raw=True,
        )
        return []

    return [
        displayed_suggestions[idx - 1]
        for idx in sorted(selected_indices)
    ]


def _build_selected_replacements(replacements, selected_suggestions):
    selected_replacements = {value: value for value in replacements.keys()}
    for value, target in selected_suggestions:
        selected_replacements[value] = target
    return selected_replacements


__all__ = [
    "build_fuzzy_mapping",
    "build_validate_attribute_mapping",
    "get_non_empty_unique_text_values",
    "has_optional_function",
    "normalize_for_compare",
    "prepare_validate_shapefile_attribute_mappings",
]
