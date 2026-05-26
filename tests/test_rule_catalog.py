import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from core.rules.catalog import (
    REQUIRED_PROFILE_COMPONENTS,
    list_rule_profile_catalog,
    resolve_rule_profile_for_theme,
)
from core.rules.loader import invalidate_rule_profile_cache


class RuleCatalogTests(unittest.TestCase):
    def tearDown(self):
        invalidate_rule_profile_cache()

    def test_resolves_theme_folder_with_profile_metadata(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            rules_base = Path(temp_dir) / "rules"
            self._write_profile(rules_base / "demo" / "perfil")

            with patch("core.rules.loader.RULES_BASE", str(rules_base)):
                invalidate_rule_profile_cache()

                resolution = resolve_rule_profile_for_theme("perfil")

        self.assertTrue(resolution.found)
        self.assertTrue(resolution.complete)
        self.assertEqual(resolution.profile_name, "demo/perfil")
        self.assertEqual(resolution.project_name, "default")
        self.assertEqual(resolution.profile_project_name, "default")
        self.assertEqual(resolution.missing_components, ())

    def test_reports_missing_required_components(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            rules_base = Path(temp_dir) / "rules"
            self._write_profile(
                rules_base / "demo" / "perfil",
                skip_components={"relations.json"},
            )

            with patch("core.rules.loader.RULES_BASE", str(rules_base)):
                invalidate_rule_profile_cache()

                resolution = resolve_rule_profile_for_theme("perfil")

        self.assertTrue(resolution.found)
        self.assertFalse(resolution.complete)
        self.assertEqual(resolution.missing_components, ("relations.json",))

    def test_lists_catalog_entries(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            rules_base = Path(temp_dir) / "rules"
            self._write_profile(rules_base / "demo" / "perfil")

            with patch("core.rules.loader.RULES_BASE", str(rules_base)):
                invalidate_rule_profile_cache()

                catalog = list_rule_profile_catalog()

        self.assertEqual(len(catalog), 1)
        self.assertEqual(catalog[0]["profile_name"], "demo/perfil")
        self.assertTrue(catalog[0]["complete"])

    def _write_profile(self, profile_dir, skip_components=None):
        skip_components = set(skip_components or ())
        profile_dir.mkdir(parents=True, exist_ok=True)
        components = {
            "profile.json": {
                "profile_name": "perfil",
                "project_name": "default",
                "theme_folder": "perfil",
            },
            "domains.json": {
                "fields": {
                    "sdb_codigo": {
                        "accepted_values": ["A"],
                        "aliases": {},
                    }
                }
            },
            "relations.json": {"relations": {}},
            "pipeline.json": {
                "auto_functions": {
                    "sdb_codigo": ["validate_shapefile_attribute"],
                }
            },
        }
        self.assertEqual(set(REQUIRED_PROFILE_COMPONENTS), set(components))
        for file_name, data in components.items():
            if file_name in skip_components:
                continue
            with (profile_dir / file_name).open("w", encoding="utf-8") as file:
                json.dump(data, file, ensure_ascii=False, indent=2)
                file.write("\n")


if __name__ == "__main__":
    unittest.main()
