import json
import tempfile
import unittest
from pathlib import Path

from core.rules.repository import RuleRepository
from core.rules.service import RuleProfileService


class RuleProfileServiceTests(unittest.TestCase):
    def test_lists_domain_values(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            profile_dir = _write_profile(Path(temp_dir))
            service = RuleProfileService(repository=RuleRepository(Path(temp_dir)))

            self.assertEqual(
                service.list_domain_values("demo/perfil", "sdb_tipo"),
                ["A", "B"],
            )
            self.assertEqual(service.resolve_profile_dir("demo/perfil"), profile_dir)

    def test_generates_categorized_style_and_validates_profile(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            _write_profile(Path(temp_dir))
            palette_path = Path(temp_dir) / "palette.md"
            palette_path.write_text(
                "\n".join(
                    [
                        "| hex | uso_localidades |",
                        "| --- | --- |",
                        "| `#111111` | A |",
                        "| `#222222` | B |",
                    ]
                ),
                encoding="utf-8",
            )
            service = RuleProfileService(repository=RuleRepository(Path(temp_dir)))

            style = service.generate_categorized_style(
                "demo/perfil",
                "sdb_tipo",
                palette_path,
                rule_name="Categorias de teste",
            )

            self.assertEqual(style["sld"]["rule_name"], "Categorias de teste")
            self.assertTrue(
                (Path(temp_dir) / "demo" / "perfil" / "style.json").exists()
            )

    def test_previews_sld(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            _write_profile(Path(temp_dir))
            service = RuleProfileService(repository=RuleRepository(Path(temp_dir)))
            output_dir = Path(temp_dir) / "preview"

            path = service.preview_sld(
                "demo/perfil",
                "camada_teste",
                output_dir=output_dir,
            )

            self.assertEqual(path, output_dir / "camada_teste.sld")
            self.assertIn(
                "<se:Name>camada_teste</se:Name>",
                path.read_text(encoding="utf-8"),
            )


def _write_profile(base_dir):
    profile_dir = base_dir / "demo" / "perfil"
    profile_dir.mkdir(parents=True, exist_ok=True)
    _write_json(
        profile_dir / "profile.json",
        {
            "profile_name": "perfil",
            "project_name": "demo",
            "theme_folder": "perfil",
        },
    )
    _write_json(
        profile_dir / "input_schema.json",
        {
            "columns": {
                "sdb_tipo": {
                    "dtype": "string",
                    "required": True,
                    "nullable": True,
                }
            }
        },
    )
    _write_json(
        profile_dir / "domains.json",
        {
            "fields": {
                "sdb_tipo": {
                    "accepted_values": ["A", "B"],
                    "aliases": {},
                }
            }
        },
    )
    _write_json(profile_dir / "relations.json", {"relations": {}})
    _write_json(
        profile_dir / "pipeline.json",
        {
            "auto_functions": {
                "sdb_tipo": ["validate_shapefile_attribute"],
            }
        },
    )
    _write_json(
        profile_dir / "style.json",
        {
            "sld": {
                "version": "1.1.0",
                "point": {
                    "fill": "#111111",
                },
            }
        },
    )
    return profile_dir


def _write_json(path, data):
    path.write_text(
        json.dumps(data, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )


if __name__ == "__main__":
    unittest.main()
