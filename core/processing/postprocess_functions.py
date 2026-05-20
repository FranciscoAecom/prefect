from importlib import import_module

from core.spatial.municipality_intersection import (
    enrich_with_municipality_intersection as _enrich_with_municipality_intersection,
)
from core.spatial.regional_bounds import enforce_car_state_bounds as _enforce_car_state_bounds
from core.utils import log, timed_log_step


_QUALIFIED_FUNCTION_CACHE = {}


def enrich_with_municipality_intersection(gdf, **context):
    return _enrich_with_municipality_intersection(gdf)


def enforce_car_state_bounds(gdf, record=None, **context):
    return _enforce_car_state_bounds(gdf, record).gdf


CORE_POSTPROCESS_FUNCTIONS = {
    "enrich_with_municipality_intersection": enrich_with_municipality_intersection,
    "enforce_car_state_bounds": enforce_car_state_bounds,
}

POSTPROCESS_FUNCTION_LABELS = {
    "enrich_with_municipality_intersection": "Intersecao com municipios",
    "enforce_car_state_bounds": "Validacao de bbox regional CAR",
}


def get_registered_postprocess_function_names():
    return set(CORE_POSTPROCESS_FUNCTIONS.keys())


def apply_postprocess_functions(gdf, profile, **context):
    for function_name in profile.get("postprocess_functions", []) or []:
        function = resolve_postprocess_function(function_name)
        if not function:
            log(f"Funcao de pos-processamento {function_name} nao registrada")
            continue

        label = POSTPROCESS_FUNCTION_LABELS.get(function_name, function_name)
        with timed_log_step(label):
            gdf = function(gdf, **context)

    return gdf


def resolve_postprocess_function(function_name):
    function = CORE_POSTPROCESS_FUNCTIONS.get(function_name)
    if function:
        return globals().get(function_name, function)

    if "." not in str(function_name):
        return None

    if function_name in _QUALIFIED_FUNCTION_CACHE:
        return _QUALIFIED_FUNCTION_CACHE[function_name]

    module_name, attr_name = str(function_name).rsplit(".", 1)
    module = import_module(module_name)
    function = getattr(module, attr_name, None)
    if function:
        _QUALIFIED_FUNCTION_CACHE[function_name] = function
    return function
