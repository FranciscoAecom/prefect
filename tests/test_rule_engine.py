import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from projects.registry import get_project_optional_functions
from core.rules.engine import (
    invalidate_rule_profile_cache,
    load_rule_profile,
    save_rule_profile,
    validate_rule_profile,
)


class ValidateRuleProfileTests(unittest.TestCase):
    def tearDown(self):
        invalidate_rule_profile_cache()

    def test_accepts_registered_short_function_names(self):
        profile = {
            "profile_name": "demo",
            "project_name": "car_reserva_legal",
            "auto_functions": {
                "sdb_cod_tema": ["validate_shapefile_attribute"],
                "sdb_des_condic": ["car_reserva_legal_transform_des_condic"],
            },
            "fields": {
                "sdb_cod_tema": {
                    "accepted_values": ["A"],
                    "aliases": {"a": "A"},
                },
                "sdb_des_condic": {
                    "accepted_values": ["Analizado"],
                    "aliases": {},
                },
            },
            "relations": {},
        }

        validate_rule_profile(
            profile,
            "car_reserva_legal/demo",
            optional_functions=get_project_optional_functions("car_reserva_legal"),
        )

    def test_legacy_project_alias_loads_new_optional_function_module(self):
        functions = get_project_optional_functions("reserva_legal_car")

        self.assertIn("car_reserva_legal_transform_des_condic", functions)
        self.assertIn("reserva_legal_car_transform_des_condic", functions)

    def test_rejects_unknown_optional_function(self):
        profile = {
            "profile_name": "demo",
            "project_name": "car_area_preservacao_permanente",
            "auto_functions": {
                "sdb_cod_tema": ["funcao_que_nao_existe"],
            },
            "fields": {
                "sdb_cod_tema": {
                    "accepted_values": ["A"],
                    "aliases": {},
                },
            },
            "relations": {},
        }

        with self.assertRaisesRegex(ValueError, "nao esta registrada"):
            validate_rule_profile(
                profile,
                "car_area_preservacao_permanente/demo",
                optional_functions=get_project_optional_functions("car_area_preservacao_permanente"),
            )

    def test_rejects_alias_target_outside_accepted_values(self):
        profile = {
            "profile_name": "demo",
            "project_name": "estado",
            "auto_functions": {},
            "fields": {
                "sdb_nm_uf": {
                    "accepted_values": ["Acre"],
                    "aliases": {"AC": "Amazonas"},
                },
            },
            "relations": {},
        }

        with self.assertRaisesRegex(ValueError, "fora de 'accepted_values'"):
            validate_rule_profile(profile, "estado/demo")

    def test_rejects_sld_literal_outside_domain(self):
        profile = {
            "profile_name": "demo",
            "project_name": "estado",
            "auto_functions": {},
            "fields": {
                "sdb_tipo": {
                    "accepted_values": ["A", "B"],
                    "aliases": {},
                },
            },
            "relations": {},
            "sld": {
                "rules": [
                    {
                        "name": "A",
                        "filter": {"property": "sdb_tipo", "literal": "A"},
                        "point": {"fill": "#111111"},
                    },
                    {
                        "name": "C",
                        "filter": {"property": "sdb_tipo", "literal": "C"},
                        "point": {"fill": "#222222"},
                    },
                ]
            },
        }

        with self.assertRaisesRegex(ValueError, "fora do dominio"):
            validate_rule_profile(profile, "estado/demo")

    def test_rejects_sld_missing_domain_literal(self):
        profile = {
            "profile_name": "demo",
            "project_name": "estado",
            "auto_functions": {},
            "fields": {
                "sdb_tipo": {
                    "accepted_values": ["A", "B"],
                    "aliases": {},
                },
            },
            "relations": {},
            "sld": {
                "rules": [
                    {
                        "name": "A",
                        "filter": {"property": "sdb_tipo", "literal": "A"},
                        "point": {"fill": "#111111"},
                    },
                ]
            },
        }

        with self.assertRaisesRegex(ValueError, "nao cobre todos os valores"):
            validate_rule_profile(profile, "estado/demo")

    def test_rejects_invalid_modular_input_schema_component(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            profile_dir = Path(temp_dir) / "rules" / "demo" / "perfil"
            self._write_modular_profile(
                profile_dir,
                input_schema={
                    "columns": {
                        "sdb_codigo": {
                            "dtype": "string",
                            "required": "sim",
                        }
                    }
                },
            )

            with patch("core.rules.engine.RULES_BASE", str(Path(temp_dir) / "rules")):
                invalidate_rule_profile_cache()
                with self.assertRaisesRegex(ValueError, "input_schema.json"):
                    load_rule_profile("demo/perfil")

    def test_rejects_invalid_modular_profile_component(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            profile_dir = Path(temp_dir) / "rules" / "demo" / "perfil"
            self._write_modular_profile(profile_dir)
            self._write_json(
                profile_dir / "profile.json",
                {
                    "project_name": "demo",
                    "theme_folder": "perfil",
                },
            )

            with patch("core.rules.engine.RULES_BASE", str(Path(temp_dir) / "rules")):
                invalidate_rule_profile_cache()
                with self.assertRaisesRegex(ValueError, "profile.json"):
                    load_rule_profile("demo/perfil")

    def test_rejects_invalid_modular_domains_component(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            profile_dir = Path(temp_dir) / "rules" / "demo" / "perfil"
            self._write_modular_profile(
                profile_dir,
                domains={
                    "fields": {
                        "sdb_codigo": {
                            "accepted_values": "A",
                            "aliases": {},
                        }
                    }
                },
            )

            with patch("core.rules.engine.RULES_BASE", str(Path(temp_dir) / "rules")):
                invalidate_rule_profile_cache()
                with self.assertRaisesRegex(ValueError, "domains.json"):
                    load_rule_profile("demo/perfil")

    def test_rejects_invalid_modular_treatment_component(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            profile_dir = Path(temp_dir) / "rules" / "demo" / "perfil"
            self._write_modular_profile(
                profile_dir,
                treatment={
                    "auto_functions": {
                        "sdb_codigo": "validate_shapefile_attribute",
                    }
                },
            )

            with patch("core.rules.engine.RULES_BASE", str(Path(temp_dir) / "rules")):
                invalidate_rule_profile_cache()
                with self.assertRaisesRegex(ValueError, "treatment.json"):
                    load_rule_profile("demo/perfil")

    def test_rejects_invalid_quality_outputs_component(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            profile_dir = Path(temp_dir) / "rules" / "demo" / "perfil"
            self._write_modular_profile(
                profile_dir,
                treatment={
                    "auto_functions": {
                        "sdb_codigo": ["validate_shapefile_attribute"],
                    },
                    "quality_outputs": {
                        "geometric_duplicates": "sim",
                    },
                },
            )

            with patch("core.rules.engine.RULES_BASE", str(Path(temp_dir) / "rules")):
                invalidate_rule_profile_cache()
                with self.assertRaisesRegex(ValueError, "quality_outputs"):
                    load_rule_profile("demo/perfil")

    def test_rejects_modular_style_outside_domain(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            profile_dir = Path(temp_dir) / "rules" / "demo" / "perfil"
            self._write_modular_profile(
                profile_dir,
                style={
                    "sld": {
                        "rules": [
                            {
                                "name": "B",
                                "filter": {"property": "sdb_codigo", "literal": "B"},
                                "point": {"fill": "#111111"},
                            },
                        ]
                    }
                },
            )

            with patch("core.rules.engine.RULES_BASE", str(Path(temp_dir) / "rules")):
                invalidate_rule_profile_cache()
                with self.assertRaisesRegex(ValueError, "style.json"):
                    load_rule_profile("demo/perfil")

    def test_save_rule_profile_updates_modular_components(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            rules_base = Path(temp_dir) / "rules"
            profile_dir = rules_base / "demo" / "perfil"
            self._write_modular_profile(profile_dir)

            with patch("core.rules.engine.RULES_BASE", str(rules_base)):
                invalidate_rule_profile_cache()
                profile = load_rule_profile("demo/perfil")
                profile["fields"]["sdb_codigo"]["accepted_values"].append("B")
                profile["fields"]["sdb_nome"] = {
                    "accepted_values": ["Alpha"],
                    "aliases": {},
                }
                profile["relations"]["codigo_to_nome"] = {"A": "Alpha"}
                profile["postprocess_functions"] = [
                    "enrich_with_municipality_intersection"
                ]
                profile["quality_outputs"] = {
                    "attribute_duplicates": False,
                    "geometric_duplicates": True,
                }
                profile["sld"] = {
                    "rule_name": "Single symbol",
                    "point": {
                        "fill": "#1654ad",
                    },
                }

                saved_path = save_rule_profile("demo/perfil", profile)

                self.assertEqual(Path(saved_path), profile_dir)
                self.assertFalse((rules_base / "demo" / "perfil.json").exists())
                domains = json.loads((profile_dir / "domains.json").read_text(encoding="utf-8"))
                relations = json.loads((profile_dir / "relations.json").read_text(encoding="utf-8"))
                treatment = json.loads((profile_dir / "treatment.json").read_text(encoding="utf-8"))
                style = json.loads((profile_dir / "style.json").read_text(encoding="utf-8"))
                self.assertIn("B", domains["fields"]["sdb_codigo"]["accepted_values"])
                self.assertEqual(
                    relations["relations"]["codigo_to_nome"],
                    {"A": "Alpha"},
                )
                self.assertEqual(
                    treatment["postprocess_functions"],
                    ["enrich_with_municipality_intersection"],
                )
                self.assertNotIn("secondary_outputs", treatment)
                self.assertEqual(
                    treatment["quality_outputs"],
                    {
                        "attribute_duplicates": False,
                        "geometric_duplicates": True,
                    },
                )
                self.assertNotIn("sld", treatment)
                self.assertEqual(style["sld"]["point"]["fill"], "#1654ad")

    def test_autos_infracao_profile_has_only_output_adjustments(self):
        profile = load_rule_profile("autos_infracao/autos_infracao")

        self.assertNotIn("secondary_outputs", profile)
        self.assertTrue(
            profile["output_adjustments"]["relocate_outside_brazil_bounds_to_centroid"]
        )

    def test_rejects_deprecated_secondary_outputs_treatment_component(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            profile_dir = Path(temp_dir) / "rules" / "demo" / "perfil"
            self._write_modular_profile(
                profile_dir,
                treatment={
                    "secondary_outputs": ["deprecated_output"],
                    "auto_functions": {
                        "sdb_codigo": ["validate_shapefile_attribute"],
                    },
                },
            )

            with patch("core.rules.engine.RULES_BASE", str(Path(temp_dir) / "rules")):
                invalidate_rule_profile_cache()
                with self.assertRaisesRegex(ValueError, "secondary_outputs"):
                    load_rule_profile("demo/perfil")

    def test_rejects_deprecated_primary_output_treatment_component(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            profile_dir = Path(temp_dir) / "rules" / "demo" / "perfil"
            self._write_modular_profile(
                profile_dir,
                treatment={
                    "primary_output": {
                        "relocate_outside_brazil_bounds_to_centroid": True,
                    },
                    "auto_functions": {
                        "sdb_codigo": ["validate_shapefile_attribute"],
                    },
                },
            )

            with patch("core.rules.engine.RULES_BASE", str(Path(temp_dir) / "rules")):
                invalidate_rule_profile_cache()
                with self.assertRaisesRegex(ValueError, "output_adjustments"):
                    load_rule_profile("demo/perfil")

    def _write_modular_profile(
        self,
        profile_dir,
        input_schema=None,
        domains=None,
        relations=None,
        treatment=None,
        style=None,
    ):
        profile_dir.mkdir(parents=True, exist_ok=True)
        self._write_json(
            profile_dir / "profile.json",
            {
                "profile_name": "perfil",
                "project_name": "demo",
                "theme_folder": "perfil",
            },
        )
        self._write_json(
            profile_dir / "input_schema.json",
            input_schema
            if input_schema is not None
            else {
                "columns": {
                    "sdb_codigo": {
                        "dtype": "string",
                        "required": True,
                        "nullable": True,
                    }
                }
            },
        )
        self._write_json(
            profile_dir / "domains.json",
            domains
            if domains is not None
            else {
                "fields": {
                    "sdb_codigo": {
                        "accepted_values": ["A"],
                        "aliases": {},
                    }
                }
            },
        )
        self._write_json(
            profile_dir / "relations.json",
            relations if relations is not None else {"relations": {}},
        )
        self._write_json(
            profile_dir / "treatment.json",
            treatment
            if treatment is not None
            else {
                "auto_functions": {
                    "sdb_codigo": ["validate_shapefile_attribute"],
                }
            },
        )
        if style is not None:
            self._write_json(profile_dir / "style.json", style)

    def _write_json(self, path, data):
        with path.open("w", encoding="utf-8") as file:
            json.dump(data, file, ensure_ascii=False, indent=2)
            file.write("\n")
