import unittest

from core.rules.validators.domains import validate_domains_component
from core.rules.validators.input_schema import validate_input_schema_component
from core.rules.validators.pipeline import validate_pipeline_component
from core.rules.validators.profile import validate_profile_component
from core.rules.validators.relations import validate_relations_component
from core.rules.validators.style import validate_style_component


class RuleValidatorTests(unittest.TestCase):
    def test_profile_component_requires_profile_name(self):
        with self.assertRaisesRegex(ValueError, "profile_name"):
            validate_profile_component(
                {"theme_folder": "demo", "project_name": "demo"},
                "demo",
            )

    def test_input_schema_component_rejects_invalid_columns_shape(self):
        with self.assertRaisesRegex(ValueError, "columns"):
            validate_input_schema_component({"columns": []})

    def test_domains_component_rejects_alias_outside_accepted_values(self):
        with self.assertRaisesRegex(ValueError, "fora de 'accepted_values'"):
            validate_domains_component(
                {
                    "fields": {
                        "sdb_codigo": {
                            "accepted_values": ["A"],
                            "aliases": {"apelido": "B"},
                        }
                    }
                }
            )

    def test_domains_component_rejects_mojibake_in_accepted_values(self):
        with self.assertRaisesRegex(ValueError, "possivel mojibake"):
            validate_domains_component(
                {
                    "fields": {
                        "sdb_uc": {
                            "accepted_values": ["ESTAÃ\u0087Ã\u0083O ECOLÃ\u0093GICA"],
                            "aliases": {},
                        }
                    }
                }
            )

    def test_relations_component_rejects_unknown_relation_field(self):
        with self.assertRaisesRegex(ValueError, "origem nao configurado"):
            validate_relations_component(
                {"uf_to_municipio": {"BA": "Salvador"}},
                {"sdb_estado": {"accepted_values": ["BA"]}},
            )

    def test_pipeline_component_rejects_deprecated_sld_entry(self):
        with self.assertRaisesRegex(ValueError, "style.json"):
            validate_pipeline_component(
                {"sld": {"point": {"fill": "#fff"}}},
                {},
            )

    def test_style_component_rejects_sld_literal_outside_domain(self):
        with self.assertRaisesRegex(ValueError, "fora do dominio"):
            validate_style_component(
                {
                    "sld": {
                        "rules": [
                            {
                                "filter": {
                                    "property": "sdb_codigo",
                                    "literal": "B",
                                }
                            }
                        ]
                    }
                },
                {"sdb_codigo": {"accepted_values": ["A"]}},
            )


if __name__ == "__main__":
    unittest.main()
