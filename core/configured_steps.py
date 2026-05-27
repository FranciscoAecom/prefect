from dataclasses import dataclass
from importlib import import_module

from core.spatial.municipality_intersection import enrich_with_municipality_intersection
from core.spatial.regional_bounds import (
    enforce_car_state_bounds as _regional_enforce_car_state_bounds,
)


@dataclass(frozen=True)
class ConfiguredStep:
    name: str
    function: object
    label: str | None = None


_QUALIFIED_FUNCTION_CACHE = {}


def _enrich_with_municipality_intersection(gdf, **context):
    return enrich_with_municipality_intersection(gdf)


def _enforce_car_state_bounds(gdf, record=None, **context):
    return _regional_enforce_car_state_bounds(gdf, record).gdf


POSTPROCESS_STEPS = {
    "enrich_with_municipality_intersection": ConfiguredStep(
        name="enrich_with_municipality_intersection",
        function=_enrich_with_municipality_intersection,
        label="Intersecao com municipios",
    ),
    "enforce_car_state_bounds": ConfiguredStep(
        name="enforce_car_state_bounds",
        function=_enforce_car_state_bounds,
        label="Validacao de bbox regional CAR",
    ),
}


def get_registered_postprocess_function_names():
    return set(POSTPROCESS_STEPS.keys())


def resolve_postprocess_step(name):
    step = POSTPROCESS_STEPS.get(name)
    if step:
        return step

    function = resolve_qualified_function(name)
    if function:
        return ConfiguredStep(name=name, function=function, label=name)
    return None

def resolve_qualified_function(name):
    if "." not in str(name):
        return None

    if name in _QUALIFIED_FUNCTION_CACHE:
        return _QUALIFIED_FUNCTION_CACHE[name]

    try:
        module_name, function_name = str(name).rsplit(".", 1)
        module = import_module(module_name)
    except ModuleNotFoundError:
        return None

    function = getattr(module, function_name, None)
    if function:
        _QUALIFIED_FUNCTION_CACHE[name] = function
    return function
