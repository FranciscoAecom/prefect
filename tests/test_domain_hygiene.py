import unittest

from core.rules.domain_hygiene import build_accepted_values_and_aliases


class DomainHygieneTests(unittest.TestCase):
    def test_broken_dash_separator_becomes_alias_not_accepted_value(self):
        accepted_values, aliases = build_accepted_values_and_aliases(
            ["Ilheus", "Ilheus \u00bf Itabuna"]
        )

        self.assertIn("Ilheus - Itabuna", accepted_values)
        self.assertNotIn("Ilheus \u00bf Itabuna", accepted_values)
        self.assertEqual(aliases["Ilheus \u00bf Itabuna"], "Ilheus - Itabuna")


if __name__ == "__main__":
    unittest.main()
