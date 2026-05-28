import json
import unittest
from pathlib import Path


PROFILE_DIR = Path("rules") / "setor_censitario" / "setor_censitario"


def _load_json(name):
    return json.loads((PROFILE_DIR / name).read_text(encoding="utf-8"))


class SetorCensitarioRulesTest(unittest.TestCase):
    def test_pipeline_validates_only_controlled_domains(self):
        pipeline = _load_json("pipeline.json")

        self.assertEqual(
            set(pipeline["auto_functions"]),
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
        self.assertNotIn("sdb_cd_mun", pipeline["auto_functions"])
        self.assertNotIn("sdb_nm_mun", pipeline["auto_functions"])

    def test_relations_do_not_include_order_paired_municipality_rules(self):
        relations = _load_json("relations.json")["relations"]

        self.assertNotIn("cd_mun_to_cd_uf", relations)
        self.assertEqual(relations["cd_uf_to_nm_uf"]["11"], "Rondônia")
        self.assertEqual(relations["cd_uf_to_nm_uf"]["35"], "São Paulo")
        self.assertEqual(relations["cd_regiao_to_nm_regiao"]["1"], "Norte")
        self.assertEqual(relations["cd_sit_to_situacao"]["1"], "Urbana")
        self.assertEqual(relations["cd_sit_to_situacao"]["8"], "Rural")


if __name__ == "__main__":
    unittest.main()
