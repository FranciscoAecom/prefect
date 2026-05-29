from core.rules.config import DEFAULT_RULE_PROFILE
from core.rules.normalization import normalize_profile_name
from core.rules.validators.common import validate_component_errors


def validate_profile_component(profile, normalized_profile_name):
    errors = []
    if not profile:
        errors.append("profile.json deve conter metadados do perfil.")
    if "profile_name" not in profile:
        errors.append("Campo 'profile_name' e obrigatorio em profile.json.")
    if "theme_folder" not in profile:
        errors.append("Campo 'theme_folder' e obrigatorio em profile.json.")
    validate_profile_name_entry(profile, normalized_profile_name, errors)
    validate_theme_folder_entry(profile, normalized_profile_name, errors)
    validate_project_name_entry(profile, errors)
    validate_component_errors("profile.json", errors)


def validate_profile_name_entry(profile, normalized_profile_name, errors):
    profile_name = profile.get("profile_name")
    if profile_name is None:
        return

    if not isinstance(profile_name, str) or not profile_name.strip():
        errors.append("Campo 'profile_name' deve ser uma string nao vazia.")


def validate_theme_folder_entry(profile, normalized_profile_name, errors):
    theme_folder = profile.get("theme_folder")
    if theme_folder is None:
        return

    normalized_theme_folder = normalize_profile_name(theme_folder)
    profile_stem = normalized_profile_name.rsplit("/", 1)[-1]

    if not normalized_theme_folder:
        errors.append("Campo 'theme_folder' deve ser uma string nao vazia.")
    elif normalized_theme_folder != profile_stem:
        errors.append(
            f"Campo 'theme_folder' deve ser '{profile_stem}' quando informado."
        )


def validate_project_name_entry(profile, errors):
    project_name = profile.get("project_name")
    if not isinstance(project_name, str) or not project_name.strip():
        errors.append("Campo 'project_name' deve ser uma string nao vazia.")
        return DEFAULT_RULE_PROFILE

    return project_name.strip()
