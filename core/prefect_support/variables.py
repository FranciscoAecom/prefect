from datetime import date
from pathlib import Path


def get_prefect_variable(name, default=None):
    try:
        from prefect.variables import Variable

        return Variable.get(name, default=default)
    except Exception:
        return default


def get_path_variable(name, default):
    value = get_prefect_variable(name, str(default))
    return Path(str(value))


def get_int_variable(name, default):
    value = get_prefect_variable(name, default)
    try:
        return int(value)
    except (TypeError, ValueError):
        return default


def get_str_variable(name, default):
    value = get_prefect_variable(name, default)
    return str(default if value is None else value)


def get_date_variable(name, default):
    value = get_prefect_variable(name, default.isoformat())
    if isinstance(value, date):
        return value
    try:
        return date.fromisoformat(str(value))
    except ValueError:
        return default


def set_prefect_variable(name, value, tags=None):
    from prefect.variables import Variable

    return Variable.set(name, value, tags=tags or ["data-pipeline"], overwrite=True)


__all__ = [
    "get_date_variable",
    "get_int_variable",
    "get_path_variable",
    "get_prefect_variable",
    "get_str_variable",
    "set_prefect_variable",
]
