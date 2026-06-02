from importlib import import_module

from core.optional_functions import get_optional_functions
from projects.configs import canonical_project_name

_PROJECT_FUNCTIONS_CACHE = {}
PROJECT_FUNCTION_MODULES = {
    "car_area_preservacao_permanente": "car_common",
    "car_reserva_legal": "car_common",
    "car_servidao_administrativa": "car_common",
    "car_uso_restrito": "car_common",
}


def _load_project_functions(project_name):
    canonical_name = canonical_project_name(project_name)
    if not canonical_name or canonical_name == "default":
        return {}
    if canonical_name in _PROJECT_FUNCTIONS_CACHE:
        return _PROJECT_FUNCTIONS_CACHE[canonical_name]

    module_name = PROJECT_FUNCTION_MODULES.get(canonical_name, canonical_name)
    try:
        project_module = import_module(f"projects.functions.{module_name}")
    except ModuleNotFoundError:
        _PROJECT_FUNCTIONS_CACHE[canonical_name] = {}
        return {}

    project_functions = getattr(project_module, "PROJECT_OPTIONAL_FUNCTIONS", {})
    if not isinstance(project_functions, dict):
        project_functions = {}

    _PROJECT_FUNCTIONS_CACHE[canonical_name] = dict(project_functions)
    return _PROJECT_FUNCTIONS_CACHE[canonical_name]


def get_project_optional_functions(project_name=None):
    functions = get_optional_functions()
    functions.update(_load_project_functions(project_name))
    return functions
