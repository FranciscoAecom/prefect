import unittest
from types import SimpleNamespace

from core.output.naming import build_final_output_base_name


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


if __name__ == "__main__":
    unittest.main()
