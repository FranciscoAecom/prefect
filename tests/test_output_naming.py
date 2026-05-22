import unittest
from types import SimpleNamespace

from core.output.naming import build_final_output_base_name
from core.output.paths import build_secondary_output_base_name


class OutputNamingTests(unittest.TestCase):
    def test_autos_infracao_uses_enov_in_output_name(self):
        record = SimpleNamespace(
            input_path="entrada.gpkg",
            source_path="origem",
            rule_profile="autos_infracao/autos_infracao",
            theme_folder="autos_infracao",
        )

        self.assertEqual(
            build_final_output_base_name(record),
            "pnt_pcd_enov_20260514",
        )

    def test_secondary_output_suffix_is_inserted_before_date_token(self):
        self.assertEqual(
            build_secondary_output_base_name("pnt_pcd_enov_20260514", "bbox_brasil"),
            "pnt_pcd_enov_bbox_brasil_20260514",
        )

    def test_secondary_output_suffix_is_appended_when_name_has_no_date_token(self):
        self.assertEqual(
            build_secondary_output_base_name("entrada_validado", "bbox_brasil"),
            "entrada_validado_bbox_brasil",
        )


if __name__ == "__main__":
    unittest.main()
