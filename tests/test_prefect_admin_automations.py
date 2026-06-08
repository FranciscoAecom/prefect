import unittest
from types import SimpleNamespace
from unittest.mock import Mock, patch

from scripts import prefect_admin


class PrefectAdminAutomationTests(unittest.TestCase):
    @patch("scripts.prefect_admin.Automation")
    @patch("scripts.prefect_admin.RunDeployment")
    @patch("scripts.prefect_admin.EventTrigger")
    @patch("scripts.prefect_admin.read_existing_automation", side_effect=ValueError)
    @patch("scripts.prefect_admin.read_first_existing_deployment")
    @patch("scripts.prefect_admin.get_client")
    def test_creates_treatment_publish_automation(
        self,
        mock_get_client,
        mock_read_deployment,
        mock_read_existing,
        mock_event_trigger,
        mock_run_deployment,
        mock_automation_cls,
    ):
        client_cm = Mock()
        client_cm.__enter__ = Mock(return_value=Mock())
        client_cm.__exit__ = Mock(return_value=False)
        mock_get_client.return_value = client_cm
        mock_read_deployment.return_value = SimpleNamespace(id="publish-deployment-id")
        automation = Mock()
        automation.create.return_value = SimpleNamespace(
            name="Tratamento concluido -> publicacao",
            id="automation-id",
        )
        mock_automation_cls.return_value = automation

        prefect_admin.create_treatment_publish_automation()

        mock_event_trigger.assert_called_once()
        self.assertEqual(
            mock_event_trigger.call_args.kwargs["expect"],
            {"dataset.treatment.completed"},
        )
        mock_run_deployment.assert_called_once_with(
            deployment_id="publish-deployment-id",
            parameters={"theme_folders": "{{ event.payload.theme_folders }}"},
        )
        automation.create.assert_called_once()


if __name__ == "__main__":
    unittest.main()
