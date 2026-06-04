import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace

from core.raster.record_processor import resolve_raster_output_path


class RasterRecordProcessorTests(unittest.TestCase):
    def test_resolves_raster_output_path_in_silver_with_tif_suffix(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            silver_dir = Path(temp_dir) / "silver" / "raster"
            record = SimpleNamespace(
                theme_folder="raster_precipitacao",
                input_path="chuva.tif",
                source_path="chuva.tif",
                rule_profile="",
                output_dir=str(silver_dir),
            )

            output_path = resolve_raster_output_path(
                record,
                str(silver_dir),
                use_configured_final_name=True,
            )

            self.assertEqual(output_path, silver_dir / "chuva_wgs84_lzw.tif")


if __name__ == "__main__":
    unittest.main()
