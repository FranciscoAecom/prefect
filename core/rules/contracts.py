from core.silver.primary_output import RELOCATE_OUTSIDE_BRAZIL_BOUNDS_KEY


PROFILE_METADATA_KEYS = {
    "profile_name",
    "project_name",
    "theme_folder",
    "description",
}

PROFILE_DATA_KEYS = {
    "input_schema",
    "fields",
    "relations",
    "auto_functions",
    "postprocess_functions",
    "primary_output",
    "quality_outputs",
    "secondary_outputs",
    "sld",
}

PIPELINE_COMPONENT_KEYS = {
    "auto_functions",
    "postprocess_functions",
    "primary_output",
    "quality_outputs",
    "secondary_outputs",
}

PRIMARY_OUTPUT_OPTIONS = {
    RELOCATE_OUTSIDE_BRAZIL_BOUNDS_KEY,
}


__all__ = [
    "PIPELINE_COMPONENT_KEYS",
    "PRIMARY_OUTPUT_OPTIONS",
    "PROFILE_DATA_KEYS",
    "PROFILE_METADATA_KEYS",
]
