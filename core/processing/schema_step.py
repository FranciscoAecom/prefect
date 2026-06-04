from core.treatment.context import replace_treatment_context as replace_context
from core.transforms.attribute_transforms import is_normalized_columns, normalize_columns
from core.utils import log
from core.validation.tabular_schema import coerce_input_schema_types, get_tabular_schema


def validate_input_schema_step(context):
    gdf = context.gdf
    if gdf is not None and not is_normalized_columns(gdf):
        gdf = normalize_columns(gdf)
        context = replace_context(context, gdf=gdf)

    if get_tabular_schema(context.rule_profile) is None:
        return context

    gdf, errors = coerce_input_schema_types(
        context.record,
        context.gdf,
        context.rule_profile,
    )
    if errors:
        message = "\n".join(f"- {error}" for error in errors)
        raise ValueError(
            f"Schema tabular invalido para {context.record.theme_folder}:\n{message}"
        )

    log(f"Validacao de schema tabular OK para {context.record.theme_folder}.")
    return replace_context(context, gdf=gdf)
