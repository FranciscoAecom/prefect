import unittest
from types import SimpleNamespace
from unittest.mock import patch

from core.validation.input_structure import validate_rule_profile_input_schema


class InputSchemaPreparationTests(unittest.TestCase):
    @patch("core.validation.input_structure.load_rule_profile")
    def test_structural_validation_uses_input_schema_and_ignores_acm_fields(
        self, mock_load_rule_profile
    ):
        mock_load_rule_profile.return_value = {
            "input_schema": {
                "columns": {
                    "sdb_codigo": {"dtype": "integer", "required": True},
                    "sdb_nome": {"dtype": "string", "required": True},
                    "acm_id": {"dtype": "integer", "required": True},
                },
                "allow_extra_columns": False,
            }
        }
        record = SimpleNamespace(rule_profile="demo/perfil", theme_folder="tema")

        result = validate_rule_profile_input_schema(
            record,
            ["sdb_codigo", "acm_id", "fid", "geometry"],
        )

        self.assertEqual(result["missing_attributes"], ["sdb_nome"])
        self.assertEqual(result["extra_attributes"], [])


if __name__ == "__main__":
    unittest.main()
