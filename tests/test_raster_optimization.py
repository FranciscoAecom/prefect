import unittest
from pathlib import Path
from unittest.mock import patch

from core.flow.flows import PREFECT_FLOWS
from core.flow.raster import raster_pipeline_flow
from core.raster.models import RasterAnalysis
from core.raster.optimization import (
    build_creation_options,
    choose_best_dtype,
    choose_overview_levels,
    choose_resampling,
    resolve_nodata,
)
from core.raster.processing import build_raster_request
from core.tasks.tasks import PREFECT_TASKS


class RasterOptimizationTests(unittest.TestCase):
    def test_choose_best_dtype_for_integer_ranges(self):
        analysis = RasterAnalysis(
            min=0,
            max=255,
            has_decimal=False,
            src_dtype_name="float32",
            valid_pixels_estimated=10,
        )

        self.assertEqual(choose_best_dtype(analysis), "uint8")

    def test_choose_best_dtype_respects_negative_and_decimal_values(self):
        signed = RasterAnalysis(
            min=-10,
            max=300,
            has_decimal=False,
            src_dtype_name="int32",
            valid_pixels_estimated=10,
        )
        decimal = RasterAnalysis(
            min=0,
            max=1,
            has_decimal=True,
            src_dtype_name="float64",
            valid_pixels_estimated=10,
        )

        self.assertEqual(choose_best_dtype(signed), "int16")
        self.assertEqual(choose_best_dtype(decimal), "float32")

    def test_choose_resampling_defaults_by_value_type(self):
        integer = RasterAnalysis(0, 1, False, "uint8", 10)
        decimal = RasterAnalysis(0, 1, True, "float32", 10)

        self.assertEqual(choose_resampling(integer), ("near", "nearest"))
        self.assertEqual(choose_resampling(decimal), ("bilinear", "average"))
        self.assertEqual(choose_resampling(integer, "cubic"), ("cubic", "average"))

    def test_choose_overview_levels_scales_by_raster_size(self):
        self.assertEqual(choose_overview_levels(512, 512), [])
        self.assertEqual(choose_overview_levels(4096, 2048), [2, 4])
        self.assertEqual(choose_overview_levels(10000, 10000), [2, 4, 8, 16])

    def test_build_creation_options_uses_predictor_by_dtype(self):
        request = build_raster_request("input.tif")

        integer_options = build_creation_options("uint16", request.options)
        float_options = build_creation_options("float32", request.options)

        self.assertIn("PREDICTOR=2", integer_options)
        self.assertIn("PREDICTOR=3", float_options)
        self.assertIn("COMPRESS=LZW", integer_options)

    def test_resolve_nodata_modes(self):
        auto = build_raster_request("input.tif", nodata_mode="auto").options
        none = build_raster_request("input.tif", nodata_mode="none").options
        custom = build_raster_request(
            "input.tif",
            nodata_mode="custom",
            custom_nodata=-9999,
        ).options

        self.assertEqual(resolve_nodata(-1, auto), -1)
        self.assertIsNone(resolve_nodata(-1, none))
        self.assertEqual(resolve_nodata(-1, custom), -9999)

    def test_build_raster_request_defaults_output_name(self):
        request = build_raster_request(Path("entrada.tif"))

        self.assertEqual(request.input_raster.name, "entrada.tif")
        self.assertEqual(request.output_raster.name, "entrada_wgs84_lzw.tif")

    @patch("core.flow.raster.optimize_raster_task")
    def test_raster_flow_calls_optimize_task(self, mock_task):
        mock_task.return_value = {"output_raster": "saida.tif"}

        result = raster_pipeline_flow.fn("entrada.tif", output_raster="saida.tif")

        self.assertEqual(result, {"output_raster": "saida.tif"})
        mock_task.assert_called_once()
        self.assertEqual(mock_task.call_args.kwargs["input_raster"], "entrada.tif")
        self.assertEqual(mock_task.call_args.kwargs["output_raster"], "saida.tif")

    def test_raster_flow_and_task_are_registered(self):
        self.assertIs(PREFECT_FLOWS["raster_pipeline"], raster_pipeline_flow)
        self.assertIn("optimize_raster", PREFECT_TASKS)


if __name__ == "__main__":
    unittest.main()
