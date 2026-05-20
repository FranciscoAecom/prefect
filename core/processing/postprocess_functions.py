from core.configured_steps import (
    get_registered_postprocess_function_names,
    resolve_postprocess_step,
)
from core.utils import log, timed_log_step


def apply_postprocess_functions(gdf, profile, **context):
    for function_name in profile.get("postprocess_functions", []) or []:
        step = resolve_postprocess_step(function_name)
        if not step:
            log(f"Funcao de pos-processamento {function_name} nao registrada")
            continue

        label = step.label or step.name
        with timed_log_step(label):
            gdf = step.function(gdf, **context)

    return gdf
