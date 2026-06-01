import unittest

from core.rules.domain_hygiene import (
    build_accepted_values_and_aliases,
    looks_like_mojibake,
    repair_utf8_mojibake,
)


class DomainHygieneTests(unittest.TestCase):
    def test_broken_dash_separator_becomes_alias_not_accepted_value(self):
        accepted_values, aliases = build_accepted_values_and_aliases(
            ["Ilheus", "Ilheus \u00bf Itabuna"]
        )

        self.assertIn("Ilheus - Itabuna", accepted_values)
        self.assertNotIn("Ilheus \u00bf Itabuna", accepted_values)
        self.assertEqual(aliases["Ilheus \u00bf Itabuna"], "Ilheus - Itabuna")

    def test_detects_utf8_mojibake(self):
        self.assertTrue(looks_like_mojibake("ESTAÃ\u0087Ã\u0083O ECOLÃ\u0093GICA"))
        self.assertFalse(looks_like_mojibake("ESTAÇÃO ECOLÓGICA"))
        self.assertFalse(looks_like_mojibake("ESTAÇÃO ECOLÓGICA DE CUNIÃ"))

    def test_repairs_utf8_mojibake(self):
        self.assertEqual(
            repair_utf8_mojibake("ESTAÃ\u0087Ã\u0083O ECOLÃ\u0093GICA"),
            "ESTAÇÃO ECOLÓGICA",
        )

    def test_mojibake_adds_repaired_value_and_alias(self):
        broken = "ESTAÃ\u0087Ã\u0083O ECOLÃ\u0093GICA"

        accepted_values, aliases = build_accepted_values_and_aliases([broken])

        self.assertEqual(accepted_values, ["ESTAÇÃO ECOLÓGICA"])
        self.assertEqual(aliases, {broken: "ESTAÇÃO ECOLÓGICA"})

        accepted_values, aliases = build_accepted_values_and_aliases(
            [broken, "ESTAÇÃO ECOLÓGICA"]
        )

        self.assertEqual(accepted_values, ["ESTAÇÃO ECOLÓGICA"])
        self.assertEqual(aliases, {broken: "ESTAÇÃO ECOLÓGICA"})


if __name__ == "__main__":
    unittest.main()
