from difflib import get_close_matches

from core.text import normalize_for_compare
from core.utils import log
from core.validation.schema import target_column_name


CONDITION_LABELS = {
    "ANALISADO": "Analisado",
    "CANCELADO": "Cancelado",
    "AGUARDANDO ANALISE": "Aguardando analise",
}


def transform_car_condition(gdf, column, **_context):
    target_column = target_column_name(column)

    if column not in gdf.columns:
        log(f"Atributo {column} nao encontrado")
        return gdf

    unique_values = gdf[column].drop_duplicates()
    replacements = {value: normalize_car_condition(value) for value in unique_values}
    gdf[target_column] = gdf[column].map(replacements)
    return gdf


def normalize_car_condition(value):
    if not isinstance(value, str):
        return value

    normalized = normalize_for_compare(value)
    if not normalized:
        return value.strip()

    for candidate, label in CONDITION_LABELS.items():
        if candidate in normalized:
            return label

    close = get_close_matches(normalized, CONDITION_LABELS, n=1, cutoff=0.8)
    if close:
        return CONDITION_LABELS[close[0]]
    return value.strip()


PROJECT_OPTIONAL_FUNCTIONS = {
    "car_area_preservacao_permanente_transform_des_condic": transform_car_condition,
    "car_app_transform_des_condic": transform_car_condition,
    "car_reserva_legal_transform_des_condic": transform_car_condition,
    "reserva_legal_car_transform_des_condic": transform_car_condition,
    "car_servidao_administrativa_transform_des_condic": transform_car_condition,
    "sa_car_transform_des_condic": transform_car_condition,
    "car_uso_restrito_transform_des_condic": transform_car_condition,
    "ur_car_transform_des_condic": transform_car_condition,
}


__all__ = ["normalize_car_condition", "transform_car_condition"]
