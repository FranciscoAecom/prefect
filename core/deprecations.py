import warnings


def warn_deprecated(old_name, new_name):
    warnings.warn(
        f"{old_name} esta depreciado; use {new_name}.",
        DeprecationWarning,
        stacklevel=3,
    )


def warn_deprecated_module(old_module, new_module):
    warn_deprecated(old_module, new_module)


__all__ = ["warn_deprecated", "warn_deprecated_module"]
