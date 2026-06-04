from core.treatment.context import TreatmentContext
from core.validation.session import ValidationSession
from projects.configs import resolve_project_config
from projects.registry import get_project_optional_functions


def build_treatment_context(record, output_dir, id_start=1):
    project_config = resolve_project_config(record.theme_folder)
    optional_functions = get_project_optional_functions(project_config["project_name"])
    return TreatmentContext(
        record=record,
        output_dir=output_dir,
        project_config=project_config,
        rule_profile_name=record.rule_profile,
        rule_profile=None,
        optional_functions=optional_functions,
        id_start=id_start,
        validation_session=ValidationSession(),
    )


__all__ = ["build_treatment_context"]
