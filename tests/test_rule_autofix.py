import unittest
from unittest.mock import patch

import pandas as pd

from core.rules.autofix import autofix_rule_profile_from_invalid_domains


class RuleAutofixTests(unittest.TestCase):
    @patch("core.rules.autofix.save_rule_profile")
    def test_persists_repaired_mojibake_as_alias(self, mock_save):
        profile = {
            "fields": {
                "sdb_uc": {
                    "accepted_values": ["ESTAÇÃO ECOLÓGICA"],
                    "aliases": {},
                }
            },
            "relations": {},
        }
        gdf = pd.DataFrame({"sdb_uc": ["ESTAÃ\u0087Ã\u0083O ECOLÃ\u0093GICA"]})

        result = autofix_rule_profile_from_invalid_domains("demo/perfil", profile, gdf)

        self.assertTrue(result["changed"])
        self.assertEqual(profile["fields"]["sdb_uc"]["accepted_values"], ["ESTAÇÃO ECOLÓGICA"])
        self.assertEqual(
            profile["fields"]["sdb_uc"]["aliases"]["ESTAÃ\u0087Ã\u0083O ECOLÃ\u0093GICA"],
            "ESTAÇÃO ECOLÓGICA",
        )
        mock_save.assert_called_once_with("demo/perfil", profile)

    @patch("core.rules.autofix.save_rule_profile")
    def test_persists_repaired_mojibake_as_new_canonical_value_and_alias(self, mock_save):
        profile = {
            "fields": {
                "sdb_uc": {
                    "accepted_values": ["ESTAÇÃO ECOLÓGICA"],
                    "aliases": {},
                }
            },
            "relations": {},
        }
        gdf = pd.DataFrame({"sdb_uc": ["PARQUE NACIONAL DO TAPAJÃ\u0093S"]})

        result = autofix_rule_profile_from_invalid_domains("demo/perfil", profile, gdf)

        self.assertTrue(result["changed"])
        self.assertIn("PARQUE NACIONAL DO TAPAJÓS", profile["fields"]["sdb_uc"]["accepted_values"])
        self.assertEqual(
            profile["fields"]["sdb_uc"]["aliases"]["PARQUE NACIONAL DO TAPAJÃ\u0093S"],
            "PARQUE NACIONAL DO TAPAJÓS",
        )
        mock_save.assert_called_once_with("demo/perfil", profile)


if __name__ == "__main__":
    unittest.main()
