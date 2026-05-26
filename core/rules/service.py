from pathlib import Path

from core.rules import loader as rule_loader
from core.rules.constants import STYLE_COMPONENT
from core.rules.generation.style import generate_categorized_style_from_domain
from core.sld.persistence import build_sld_style, render_sld


class RuleProfileService:
    def __init__(self, repository=None):
        self.repository = repository or rule_loader.get_repository()

    def resolve_profile_dir(self, profile_name):
        profile_dir = self.repository.modular_profile_path(profile_name)
        if not profile_dir.is_dir():
            raise FileNotFoundError(f"Perfil de regras nao encontrado: {profile_dir}")
        return profile_dir

    def load_profile(self, profile_name):
        return self.repository.load_rule_profile(profile_name)

    def validate_profile(self, profile_name):
        profile = self.load_profile(profile_name)
        return profile

    def list_domain_values(self, profile_name, field_name):
        profile = self.load_profile(profile_name)
        fields = profile.get("fields", {})
        field = fields.get(field_name)
        if not isinstance(field, dict):
            raise KeyError(f"Campo nao encontrado no perfil {profile_name}: {field_name}")
        values = field.get("accepted_values", [])
        if not isinstance(values, list):
            raise ValueError(f"Campo {field_name}.accepted_values deve ser uma lista.")
        return list(values)

    def generate_categorized_style(
        self,
        profile_name,
        field_name,
        palette_path,
        geometry_kind="point",
        usage_column="uso_localidades",
        default_color_value=None,
        rule_name=None,
    ):
        profile_dir = self.resolve_profile_dir(profile_name)
        style = generate_categorized_style_from_domain(
            rules_dir=profile_dir,
            field_name=field_name,
            palette_path=palette_path,
            output_path=profile_dir / STYLE_COMPONENT,
            geometry_kind=geometry_kind,
            usage_column=usage_column,
            default_color_value=default_color_value,
            rule_name=rule_name,
        )
        self.repository.invalidate(profile_name)
        self.validate_profile(profile_name)
        return style

    def preview_sld(
        self,
        profile_name,
        layer_name,
        geometry_kind="point",
        output_dir=None,
    ):
        profile = self.load_profile(profile_name)
        style = build_sld_style(profile)
        sld_text = render_sld(
            layer_name=layer_name,
            geometry_kind=geometry_kind,
            style=style,
        )
        output_dir = Path(output_dir or "output/sld_preview")
        output_dir.mkdir(parents=True, exist_ok=True)
        output_path = output_dir / f"{layer_name}.sld"
        output_path.write_text(sld_text, encoding="utf-8")
        return output_path


def build_rule_profile_service(repository=None):
    return RuleProfileService(repository=repository)


__all__ = ["RuleProfileService", "build_rule_profile_service"]
