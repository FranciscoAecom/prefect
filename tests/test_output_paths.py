import unittest
import tempfile
from pathlib import Path
from types import SimpleNamespace

from core.output.paths import resolve_output_path


class OutputPathsTests(unittest.TestCase):
    def test_versioned_record_output_dir_is_used_directly(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            output_dir = str(
                Path(temp_dir)
                / "silver_data"
                / "restricted"
                / "pcd"
                / "autos_infracao"
                / "IBAMA"
                / "20260514"
                / "00"
            )
            record = SimpleNamespace(
                theme_folder="autos_infracao",
                input_path="entrada.gpkg",
                output_dir=output_dir,
            )

            theme_output_dir, base_name, output_path = resolve_output_path(
                record,
                record.output_dir,
                use_configured_final_name=False,
            )

            self.assertEqual(theme_output_dir, record.output_dir)
            self.assertEqual(base_name, "entrada_validado")
            self.assertEqual(
                output_path,
                str(Path(output_dir) / "entrada_validado.gpkg"),
            )


if __name__ == "__main__":
    unittest.main()
