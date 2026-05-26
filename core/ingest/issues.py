from core.ingest.eligibility import (
    REASON_MISSING_SOURCE_PATH,
    REASON_ZIP_SOURCE_PATH,
    reason_message,
)
from core.ingest.models import IngestIssue

ISSUE_INPUT_DATASET_RESOLUTION_ERROR = "input_dataset_resolution_error"
ISSUE_MISSING_RULE_PROFILE = "missing_rule_profile"
ISSUE_RULE_PROFILE_INCOMPLETE = "rule_profile_incomplete"
ISSUE_RULE_PROFILE_PROJECT_INCONSISTENT = "rule_profile_project_inconsistent"
ISSUE_RULE_PROFILE_RESOLUTION_ERROR = "rule_profile_resolution_error"


def missing_source_path_issue(issue_context):
    return _ingest_issue(
        issue_context,
        code=REASON_MISSING_SOURCE_PATH,
        reason=reason_message(REASON_MISSING_SOURCE_PATH),
    )


def zip_source_path_issue(issue_context):
    return _ingest_issue(
        issue_context,
        code=REASON_ZIP_SOURCE_PATH,
        reason=reason_message(REASON_ZIP_SOURCE_PATH),
    )


def rule_profile_resolution_error_issue(issue_context, error):
    return _ingest_issue(
        issue_context,
        code=ISSUE_RULE_PROFILE_RESOLUTION_ERROR,
        reason=str(error),
    )


def missing_rule_profile_issue(issue_context, rule_resolution):
    return _ingest_issue(
        issue_context,
        code=ISSUE_MISSING_RULE_PROFILE,
        reason=(
            "Nenhum arquivo de regra correspondente foi encontrado em rules/. "
            f"Perfil esperado: rules/{rule_resolution.expected_profile_name}."
        ),
    )


def incomplete_rule_profile_issue(issue_context, rule_resolution):
    return _ingest_issue(
        issue_context,
        code=ISSUE_RULE_PROFILE_INCOMPLETE,
        reason=(
            "Perfil de regras incompleto: "
            f"{rule_resolution.profile_name} sem "
            + ", ".join(rule_resolution.missing_components)
            + "."
        ),
    )


def inconsistent_rule_profile_issue(issue_context, rule_resolution):
    return _ingest_issue(
        issue_context,
        code=ISSUE_RULE_PROFILE_PROJECT_INCONSISTENT,
        reason=(
            "Perfil de regras inconsistente com o projeto resolvido: "
            f"theme_folder={issue_context['theme_folder']} -> projeto {rule_resolution.project_name}, "
            f"mas o perfil {rule_resolution.profile_name} declara "
            f"project_name={rule_resolution.profile_project_name}."
        ),
    )


def input_dataset_resolution_error_issue(issue_context, error):
    return _ingest_issue(
        issue_context,
        code=ISSUE_INPUT_DATASET_RESOLUTION_ERROR,
        reason=str(error),
    )


def _ingest_issue(issue_context, *, code, reason):
    return IngestIssue(
        sheet_row=issue_context["sheet_row"],
        record_id=issue_context["record_id"],
        theme_folder=issue_context["theme_folder"],
        status=issue_context["status"],
        source_path=issue_context["source_path"],
        reason=reason,
        code=code,
    )


__all__ = [
    "ISSUE_INPUT_DATASET_RESOLUTION_ERROR",
    "ISSUE_MISSING_RULE_PROFILE",
    "ISSUE_RULE_PROFILE_INCOMPLETE",
    "ISSUE_RULE_PROFILE_PROJECT_INCONSISTENT",
    "ISSUE_RULE_PROFILE_RESOLUTION_ERROR",
    "incomplete_rule_profile_issue",
    "inconsistent_rule_profile_issue",
    "input_dataset_resolution_error_issue",
    "missing_rule_profile_issue",
    "missing_source_path_issue",
    "rule_profile_resolution_error_issue",
    "zip_source_path_issue",
]
