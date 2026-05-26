import unittest

from core.ingest.issues import (
    ISSUE_MISSING_RULE_PROFILE,
    ISSUE_RULE_PROFILE_INCOMPLETE,
    incomplete_rule_profile_issue,
    issue_to_dict,
    issues_to_dicts,
    missing_rule_profile_issue,
)
from core.rules.catalog import RuleProfileResolution


class IngestIssuesTests(unittest.TestCase):
    def test_missing_rule_profile_issue_keeps_message_and_code(self):
        issue = missing_rule_profile_issue(
            _issue_context(),
            RuleProfileResolution(
                theme_folder="localidades",
                normalized_theme_folder="localidades",
                project_name="localidades",
                expected_profile_name="localidades/localidades",
                profile_name=None,
                profile_dir=None,
                profile_project_name="",
            ),
        )

        self.assertEqual(issue.code, ISSUE_MISSING_RULE_PROFILE)
        self.assertIn(
            "Perfil esperado: rules/localidades/localidades.",
            issue.reason,
        )

    def test_incomplete_rule_profile_issue_keeps_missing_components(self):
        issue = incomplete_rule_profile_issue(
            _issue_context(),
            RuleProfileResolution(
                theme_folder="localidades",
                normalized_theme_folder="localidades",
                project_name="localidades",
                expected_profile_name="localidades/localidades",
                profile_name="localidades/localidades",
                profile_dir=None,
                profile_project_name="localidades",
                missing_components=("domains.json", "pipeline.json"),
            ),
        )

        self.assertEqual(issue.code, ISSUE_RULE_PROFILE_INCOMPLETE)
        self.assertIn("domains.json, pipeline.json", issue.reason)

    def test_issue_serialization_includes_code_and_reason(self):
        issue = missing_rule_profile_issue(
            _issue_context(),
            RuleProfileResolution(
                theme_folder="localidades",
                normalized_theme_folder="localidades",
                project_name="localidades",
                expected_profile_name="localidades/localidades",
                profile_name=None,
                profile_dir=None,
                profile_project_name="",
            ),
        )

        row = issue_to_dict(issue)

        self.assertEqual(row["code"], ISSUE_MISSING_RULE_PROFILE)
        self.assertEqual(row["reason"], issue.reason)
        self.assertEqual(issues_to_dicts([issue]), [row])


def _issue_context():
    return {
        "sheet_row": 2,
        "record_id": 10,
        "theme_folder": "localidades",
        "status": "Waiting Update",
        "source_path": r"L:\base.gpkg",
    }


if __name__ == "__main__":
    unittest.main()
