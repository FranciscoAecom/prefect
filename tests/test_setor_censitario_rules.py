import json
import unittest
from pathlib import Path

from core.rules.engine import classify_field_value, load_rule_profile


PROFILE_DIR = Path("rules") / "setor_censitario" / "setor_censitario"
ILHEUS_ALIAS = "Ilh\u00e9us \u00bf Itabuna"
ILHEUS_CANONICAL = "Ilh\u00e9us - Itabuna"
GOIANA_ALIAS = "Goiana \u00bf Timba\u00faba"
GOIANA_CANONICAL = "Goiana - Timba\u00faba"


def _load_json(name):
    return json.loads((PROFILE_DIR / name).read_text(encoding="utf-8"))


class SetorCensitarioRulesTest(unittest.TestCase):
    def test_treatment_validates_only_controlled_domains(self):
        treatment = _load_json("treatment.json")

        self.assertEqual(
            set(treatment["auto_functions"]),
            {
                "sdb_situacao",
                "sdb_cd_sit",
                "sdb_cd_tipo",
                "sdb_cd_regiao",
                "sdb_nm_regiao",
                "sdb_cd_uf",
                "sdb_nm_uf",
                "sdb_cd_rgint",
                "sdb_nm_rgint",
                "sdb_cd_rgi",
                "sdb_nm_rgi",
            },
        )
        self.assertNotIn("sdb_cd_mun", treatment["auto_functions"])
        self.assertNotIn("sdb_nm_mun", treatment["auto_functions"])

    def test_relations_do_not_include_order_paired_municipality_rules(self):
        relations = _load_json("relations.json")["relations"]

        self.assertNotIn("cd_mun_to_cd_uf", relations)
        self.assertEqual(relations["cd_uf_to_nm_uf"]["11"], "Rondônia")
        self.assertEqual(relations["cd_uf_to_nm_uf"]["35"], "São Paulo")
        self.assertEqual(relations["cd_regiao_to_nm_regiao"]["1"], "Norte")
        self.assertNotIn("cd_sit_to_situacao", relations)

    def test_sector_situation_domain_keeps_only_broad_situation_values(self):
        domains = _load_json("domains.json")["fields"]

        self.assertEqual(
            set(domains["sdb_situacao"]["accepted_values"]),
            {"Rural", "Urbana"},
        )
        self.assertIn("9", domains["sdb_cd_sit"]["accepted_values"])

    def test_mojibake_variants_are_aliases_not_canonical_values(self):
        domains = _load_json("domains.json")["fields"]

        self.assertNotIn(
            ILHEUS_ALIAS,
            domains["sdb_nm_rgint"]["accepted_values"],
        )
        self.assertEqual(
            domains["sdb_nm_rgint"]["aliases"][ILHEUS_ALIAS],
            ILHEUS_CANONICAL,
        )
        self.assertNotIn(
            GOIANA_ALIAS,
            domains["sdb_nm_rgi"]["accepted_values"],
        )
        self.assertEqual(
            domains["sdb_nm_rgi"]["aliases"][GOIANA_ALIAS],
            GOIANA_CANONICAL,
        )

        profile = load_rule_profile("setor_censitario/setor_censitario")
        result = classify_field_value(profile, "sdb_nm_rgi", GOIANA_ALIAS)
        self.assertEqual(result["status"], "normalized")
        self.assertEqual(result["normalized_value"], GOIANA_CANONICAL)

        for field_name, field_rules in domains.items():
            with self.subTest(field_name=field_name):
                self.assertFalse(
                    any("\u00bf" in value for value in field_rules["accepted_values"])
                )
                self.assertFalse(
                    any("\u00bf" in value for value in field_rules.get("aliases", {}).values())
                )


if __name__ == "__main__":
    unittest.main()
