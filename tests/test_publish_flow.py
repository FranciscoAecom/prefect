import unittest
from types import SimpleNamespace
from unittest.mock import patch

from core.publish.metadata import MultiplePublishItemsError
from core.publish.service import publish_record_outputs
from core.publish.service import publish_record_outputs_direct
from core.prefect_support.run_names import publish_flow_run_name_for_parameters


class PublishFlowTests(unittest.TestCase):
    def test_publish_flow_run_name_uses_theme_folder(self):
        self.assertEqual(
            publish_flow_run_name_for_parameters({"theme_folders": ["sa_car_ac"]}),
            "publish_sa_car_ac",
        )

    def test_publish_flow_run_name_uses_batch_count(self):
        self.assertEqual(
            publish_flow_run_name_for_parameters(
                {"theme_folders": ["rl_car_ac", "sa_car_ac"]}
            ),
            "publish_2_bases",
        )

    def test_publish_flow_run_name_uses_folder_when_manual(self):
        self.assertEqual(
            publish_flow_run_name_for_parameters({"folder": r"L:\silver\autos\01"}),
            "publish_01",
        )

    def test_publish_flow_run_name_uses_ingest_fallback(self):
        self.assertEqual(
            publish_flow_run_name_for_parameters({}),
            "publish_ingest",
        )

    @patch("core.flow.publish.run_data_publish")
    @patch("core.flow.publish.load_publish_folders_from_ingest")
    def test_data_publish_flow_uses_ingest_when_folder_is_not_provided(
        self,
        mock_load_folders,
        mock_run_publish,
    ):
        mock_load_folders.return_value = [r"L:\silver\autos\01"]

        from core.flow.publish import data_publish_flow

        data_publish_flow.fn(theme_folders=["autos_infracao"], dry_run=True)

        mock_load_folders.assert_called_once_with(["autos_infracao"])
        mock_run_publish.assert_called_once()
        self.assertEqual(mock_run_publish.call_args.args[0], [r"L:\silver\autos\01"])

    @patch("core.publish.service.publish_item_task")
    @patch("core.publish.service.discover_publish_items_task")
    def test_publish_record_outputs_uses_record_output_dir(
        self,
        mock_discover,
        mock_publish,
    ):
        item = SimpleNamespace(layer="pnt_pcd_enov_20260514")
        mock_discover.return_value = [item]
        record = SimpleNamespace(output_dir=r"L:\silver\autos\00")

        publish_record_outputs(
            record,
            fallback_output_dir=r"C:\fallback",
            environment="qas",
            workspace="gold",
            dry_run=True,
        )

        mock_discover.assert_called_once_with(r"L:\silver\autos\00")
        mock_publish.assert_called_once()
        self.assertIs(mock_publish.call_args.args[0], item)
        self.assertEqual(mock_publish.call_args.kwargs["environment"], "qas")
        self.assertEqual(mock_publish.call_args.kwargs["workspace"], "gold")

    @patch("core.publish.execution.import_metadata_to_geonetwork")
    @patch("core.publish.execution.publish_to_geoserver")
    @patch("core.publish.execution.discover_publish_items")
    def test_publish_record_outputs_direct_uses_plain_functions(
        self,
        mock_discover,
        mock_geoserver,
        mock_geonetwork,
    ):
        item = SimpleNamespace(layer="pnt_pcd_enov_20260514")
        config = SimpleNamespace()
        credentials = SimpleNamespace()
        mock_discover.return_value = [item]
        mock_geoserver.return_value = {"sdb_cod_tema": "String"}

        publish_record_outputs_direct(
            r"L:\silver\autos\00",
            config,
            credentials,
            dry_run=True,
        )

        mock_discover.assert_called_once_with(r"L:\silver\autos\00")
        mock_geoserver.assert_called_once_with(
            item,
            config,
            credentials,
            dry_run=True,
            skip_data=False,
        )
        mock_geonetwork.assert_called_once_with(
            item,
            config,
            credentials,
            dry_run=True,
            attribute_types={"sdb_cod_tema": "String"},
        )

    @patch("core.publish.execution.log")
    @patch("core.publish.execution.import_metadata_to_geonetwork")
    @patch("core.publish.execution.publish_to_geoserver")
    @patch("core.publish.execution.discover_publish_items")
    def test_publish_record_outputs_direct_logs_and_skips_multiple_sets(
        self,
        mock_discover,
        mock_geoserver,
        mock_geonetwork,
        mock_log,
    ):
        mock_discover.side_effect = MultiplePublishItemsError("multiplos conjuntos")

        publish_record_outputs_direct(
            r"L:\silver\autos\00",
            SimpleNamespace(),
            SimpleNamespace(),
            dry_run=True,
        )

        mock_log.assert_any_call("multiplos conjuntos")
        mock_geoserver.assert_not_called()
        mock_geonetwork.assert_not_called()


if __name__ == "__main__":
    unittest.main()
