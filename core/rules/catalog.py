from dataclasses import dataclass
from pathlib import Path

from projects.configs import canonical_project_name, resolve_project_name
from core.rules import loader as _rule_loader
from core.rules.constants import (
    DOMAINS_COMPONENT,
    PROFILE_COMPONENT,
    RELATIONS_COMPONENT,
    TREATMENT_COMPONENT,
)
from core.rules.normalization import (
    RuleProfileResolutionError,
    normalize_profile_name,
)


REQUIRED_PROFILE_COMPONENTS = (
    PROFILE_COMPONENT,
    DOMAINS_COMPONENT,
    RELATIONS_COMPONENT,
    TREATMENT_COMPONENT,
)


@dataclass(frozen=True)
class RuleProfileResolution:
    theme_folder: str
    normalized_theme_folder: str
    project_name: str
    expected_profile_name: str | None
    profile_name: str | None
    profile_dir: Path | None
    profile_project_name: str
    missing_components: tuple[str, ...] = ()
    error: str = ""

    @property
    def found(self):
        return bool(self.profile_name)

    @property
    def complete(self):
        return self.found and not self.missing_components

    @property
    def project_consistent(self):
        return (
            not self.profile_project_name
            or canonical_project_name(self.profile_project_name) == self.project_name
        )


def resolve_rule_profile_for_theme(theme_folder, raise_on_error=True):
    repository = _rule_loader.get_repository()
    normalized_theme_folder = normalize_profile_name(theme_folder)
    project_name = resolve_project_name(normalized_theme_folder)
    expected_profile_name = repository.expected_rule_profile_name(normalized_theme_folder)

    if not normalized_theme_folder:
        return RuleProfileResolution(
            theme_folder=str(theme_folder or ""),
            normalized_theme_folder="",
            project_name=project_name,
            expected_profile_name=expected_profile_name,
            profile_name=None,
            profile_dir=None,
            profile_project_name="",
            error="theme_folder vazio.",
        )

    try:
        profile_name = repository.find_rule_profile_by_theme_folder(normalized_theme_folder)
    except RuleProfileResolutionError as exc:
        if raise_on_error:
            raise
        return RuleProfileResolution(
            theme_folder=str(theme_folder or ""),
            normalized_theme_folder=normalized_theme_folder,
            project_name=project_name,
            expected_profile_name=expected_profile_name,
            profile_name=None,
            profile_dir=None,
            profile_project_name="",
            error=str(exc),
        )

    if not profile_name:
        return RuleProfileResolution(
            theme_folder=str(theme_folder or ""),
            normalized_theme_folder=normalized_theme_folder,
            project_name=project_name,
            expected_profile_name=expected_profile_name,
            profile_name=None,
            profile_dir=None,
            profile_project_name="",
        )

    profile_dir = repository.modular_profile_path(profile_name)
    missing_components = tuple(
        component
        for component in REQUIRED_PROFILE_COMPONENTS
        if not (profile_dir / component).exists()
    )
    profile_project_name = repository.get_rule_profile_project_name(profile_name)

    return RuleProfileResolution(
        theme_folder=str(theme_folder or ""),
        normalized_theme_folder=normalized_theme_folder,
        project_name=project_name,
        expected_profile_name=expected_profile_name,
        profile_name=profile_name,
        profile_dir=profile_dir,
        profile_project_name=profile_project_name,
        missing_components=missing_components,
    )


def list_rule_profile_catalog():
    repository = _rule_loader.get_repository()
    entries = []
    for profile_name in repository.list_rule_profiles():
        profile_dir = repository.modular_profile_path(profile_name)
        missing_components = tuple(
            component
            for component in REQUIRED_PROFILE_COMPONENTS
            if not (profile_dir / component).exists()
        )
        entries.append(
            {
                "profile_name": profile_name,
                "profile_dir": profile_dir,
                "project_name": repository.get_rule_profile_project_name(profile_name),
                "missing_components": missing_components,
                "complete": not missing_components,
            }
        )
    return entries


__all__ = [
    "REQUIRED_PROFILE_COMPONENTS",
    "RuleProfileResolution",
    "list_rule_profile_catalog",
    "resolve_rule_profile_for_theme",
]
