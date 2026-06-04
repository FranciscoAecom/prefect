import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace

from core.bronze.persistence import ensure_bronze_dataset


class BronzePersistenceTests(unittest.TestCase):
    def test_copies_raw_directory_to_bronze_when_empty(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_dir = Path(temp_dir)
            source_dir = temp_dir / "temp" / "raw"
            bronze_dir = temp_dir / "bronze" / "00"
            source_dir.mkdir(parents=True)
            (source_dir / "base.shp").write_text("shp", encoding="utf-8")
            (source_dir / "base.dbf").write_text("dbf", encoding="utf-8")
            (source_dir / "base.shx").write_text("shx", encoding="utf-8")
            (source_dir / "wfsrequest.txt").write_text("request", encoding="utf-8")
            (source_dir / "md_base.xml").write_text("old metadata", encoding="utf-8")
            record = SimpleNamespace(
                source_path=str(source_dir),
                input_path=str(source_dir / "base.shp"),
                bronze_dir=str(bronze_dir),
            )

            bronze_dataset = ensure_bronze_dataset(record)

            self.assertEqual(bronze_dataset, bronze_dir / "base.shp")
            self.assertTrue((bronze_dir / "base.dbf").exists())
            self.assertTrue((bronze_dir / "base.shx").exists())
            self.assertTrue((bronze_dir / "wfsrequest.txt").exists())
            self.assertFalse((bronze_dir / "md_base.xml").exists())

    def test_keeps_existing_bronze_dataset(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_dir = Path(temp_dir)
            source_dir = temp_dir / "temp"
            bronze_dir = temp_dir / "bronze"
            source_dir.mkdir()
            bronze_dir.mkdir()
            (source_dir / "source.gpkg").write_text("source", encoding="utf-8")
            (bronze_dir / "existing.gpkg").write_text("existing", encoding="utf-8")
            record = SimpleNamespace(
                source_path=str(source_dir),
                input_path=str(source_dir / "source.gpkg"),
                bronze_dir=str(bronze_dir),
            )

            bronze_dataset = ensure_bronze_dataset(record)

            self.assertEqual(bronze_dataset, bronze_dir / "existing.gpkg")
            self.assertFalse((bronze_dir / "source.gpkg").exists())

    def test_copies_raster_to_bronze_when_empty(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_dir = Path(temp_dir)
            source_path = temp_dir / "temp" / "chuva.tif"
            bronze_dir = temp_dir / "bronze"
            source_path.parent.mkdir()
            source_path.write_bytes(b"raster")
            record = SimpleNamespace(
                source_path=str(source_path),
                input_path=str(source_path),
                bronze_dir=str(bronze_dir),
            )

            bronze_dataset = ensure_bronze_dataset(record)

            self.assertEqual(bronze_dataset, bronze_dir / "chuva.tif")
            self.assertTrue((bronze_dir / "chuva.tif").exists())


if __name__ == "__main__":
    unittest.main()
