import unittest
from pathlib import Path
from unittest.mock import patch

from core.config.defaults import DEFAULT_DATA_LAKE_BASE
from core.config.settings import PathSettings


class PathSettingsTests(unittest.TestCase):
    def test_data_lake_base_defaults_to_shared_data_lake(self):
        with patch.dict("os.environ", {}, clear=True):
            self.assertEqual(PathSettings().data_lake_base, DEFAULT_DATA_LAKE_BASE)

    def test_output_base_follows_data_lake_base(self):
        expected = Path(r"X:\custom\data_lake")
        with patch.dict("os.environ", {"DATA_LAKE_BASE": str(expected)}):
            settings = PathSettings()

            self.assertEqual(settings.data_lake_base, expected)
            self.assertEqual(settings.output_base, expected)


if __name__ == "__main__":
    unittest.main()
