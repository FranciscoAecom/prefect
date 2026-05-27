from importlib import import_module

from core.optional_functions import get_optional_functions
from projects.configs import canonical_project_name

_PROJECT_FUNCTIONS_CACHE = {}


def _load_project_functions(project_name):
    canonical_name = canonical_project_name(project_name)
    if not canonical_name or canonical_name == "default":
        return {}
    if canonical_name in _PROJECT_FUNCTIONS_CACHE:
        return _PROJECT_FUNCTIONS_CACHE[canonical_name]

    try:
        project_module = import_module(f"projects.functions.{canonical_name}")
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
