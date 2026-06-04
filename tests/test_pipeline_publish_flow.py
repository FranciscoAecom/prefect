import unittest
from types import SimpleNamespace
from unittest.mock import patch

from core.publish.metadata import MultiplePublishItemsError
from core.flow.pipeline_publish import publish_record_outputs
from core.flow.pipeline_publish import publish_record_outputs_direct


class PipelinePublishFlowTests(unittest.TestCase):
    @patch("core.flow.pipeline_publish.publish_item_task")
    @patch("core.flow.pipeline_publish.discover_publish_items_task")
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
