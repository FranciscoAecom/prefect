import unittest

from core.optional_functions import build_pipeline_operations
from core.processing.operations import infer_operation_kind


def _noop(gdf, column, **context):
    return gdf


class PipelineOperationTests(unittest.TestCase):
    def test_infers_operation_kind_from_function_name(self):
        self.assertEqual(infer_operation_kind("validate_date_fields"), "validation")
        self.assertEqual(
            infer_operation_kind("car_area_preservacao_permanente_transform_des_condic"),
            "transform",
        )

    def test_builds_operations_from_mapping(self):
        operations = build_pipeline_operations(
            {"sdb_des_condic": ["car_area_preservacao_permanente_transform_des_condic"]},
            optional_functions={
                "car_area_preservacao_permanente_transform_des_condic": _noop,
            },
        )

        operation = operations["sdb_des_condic"][0]
        self.assertEqual(
            operation.name,
            "car_area_preservacao_permanente_transform_des_condic",
        )
        self.assertEqual(operation.kind, "transform")
        self.assertEqual(operation.source_column, "sdb_des_condic")
        self.assertEqual(operation.target_column, "acm_des_condic")


if __name__ == "__main__":
    unittest.main()
