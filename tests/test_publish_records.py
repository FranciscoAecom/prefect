import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

import pandas as pd

from core.publish.records import load_publish_records


class PublishRecordsTests(unittest.TestCase):
    @patch("core.publish.records.pd.read_excel")
    def test_loads_publish_flags_and_latest_silver_version(self, mock_read_excel):
        with tempfile.TemporaryDirectory() as temp_dir:
            base = Path(temp_dir)
            mock_read_excel.return_value = pd.DataFrame(
                [
                    {
                        "ID": 1,
                        "theme_folder": "autos_infracao",
                        "status": "treatment-publish",
                        "access_constraints": "restricted",
                        "category_acronym": "pcd",
                        "citation": "IBAMA",
                        "date": "2026-05-14",
                    },
                    {
                        "ID": 2,
                        "theme_folder": "estado",
                        "status": "treatment",
                    },
                ]
            )
            silver = (
                base
                / "silver_data"
                / "restricted"
                / "pcd"
                / "autos_infracao"
                / "IBAMA"
                / "20260514"
            )
            (silver / "00").mkdir(parents=True)
            (silver / "01").mkdir()
            (silver / "01" / "pnt_pcd_enov_20260514.gpkg").write_text("", encoding="utf-8")

            with patch("core.publish.records.DATA_LAKE_BASE", base):
                records, issues, summary = load_publish_records()

            self.assertEqual(issues, [])
            self.assertEqual(summary["publish_candidates"], 1)
            self.assertEqual(len(records), 1)
            self.assertEqual(records[0].silver_dir, str(silver / "01"))


if __name__ == "__main__":
    unittest.main()
