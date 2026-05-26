import json
import tempfile
import unittest
from pathlib import Path

from core.rules.generation.style import (
    build_categorized_sld_style,
    generate_categorized_style_from_domain,
    load_palette_assignments,
)


class StyleGenerationTests(unittest.TestCase):
    def test_builds_categorized_point_style(self):
        style = build_categorized_sld_style(
            field_name="sdb_tipo",
            values=["A", "B"],
            palette_colors=["#111111", "#222222"],
            geometry_kind="point",
        )

        self.assertEqual(len(style["sld"]["rules"]), 2)
        self.assertEqual(style["sld"]["rules"][0]["filter"]["property"], "sdb_tipo")
        self.assertEqual(style["sld"]["rules"][1]["point"]["fill"], "#222222")

    def test_loads_palette_assignments_from_markdown(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            palette_path = Path(temp_dir) / "palette.md"
            palette_path.write_text(
                "\n".join(
                    [
                        "| hex | uso_localidades |",
                        "| --- | --- |",
                        "| `#123abc` | Cidade |",
                    ]
                ),
                encoding="utf-8",
            )

            self.assertEqual(
                load_palette_assignments(palette_path),
                {"Cidade": "#123ABC"},
            )

    def test_generates_style_from_domain_and_palette_file(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            rules_dir = Path(temp_dir)
            (rules_dir / "domains.json").write_text(
                json.dumps(
                    {
                        "fields": {
                            "sdb_tipo": {
                                "accepted_values": ["A", "B"],
                                "aliases": {},
                            }
                        }
                    },
                    ensure_ascii=False,
                ),
                encoding="utf-8",
            )
            palette_path = rules_dir / "palette.md"
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

            style = generate_categorized_style_from_domain(
                rules_dir=rules_dir,
                field_name="sdb_tipo",
                palette_path=palette_path,
                default_color_value="B",
            )

            self.assertEqual(style["sld"]["point"]["fill"], "#222222")
            self.assertTrue((rules_dir / "style.json").exists())


if __name__ == "__main__":
    unittest.main()
