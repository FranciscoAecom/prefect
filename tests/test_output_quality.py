import unittest
from unittest.mock import patch

import geopandas as gpd
from shapely.geometry import Point

from core.output.quality import (
    OutputQualitySummary,
    build_output_quality_summary,
    log_output_quality_summary,
)


class OutputQualityTests(unittest.TestCase):
    @patch("core.output.quality.log")
    def test_logs_mandatory_quality_checks(self, mock_log):
        summary = OutputQualitySummary(
            attr_count=0,
            geom_count=0,
            ogc_invalid_count=0,
            safe_null_count=0,
            attr_report=None,
            geom_report=None,
            ogc_report=None,
            ogc_error_summary={},
        )

        log_output_quality_summary(summary)

        messages = [call.args[0] for call in mock_log.call_args_list]
        self.assertIn(
            (
                "Verificacoes obrigatorias de qualidade executadas: "
                "check_attribute_duplicates, check_geometric_duplicates, "
                "check_ogc_invalid_geometries"
            ),
            messages,
        )

    @patch("core.output.quality.EXPORT_OUTPUT_QUALITY_REPORT_FILES", False)
    @patch("core.output.quality.export_duplicate_reports")
    def test_does_not_export_quality_report_files_when_flag_disabled(self, mock_export):
        gdf = gpd.GeoDataFrame(
            {
                "sdb_codigo": ["A", "A"],
                "geometry": [Point(0, 0), Point(0, 0)],
            },
            geometry="geometry",
            crs="EPSG:4326",
        )

        summary = build_output_quality_summary(gdf, ".", "pnt_teste")

        mock_export.assert_not_called()
        self.assertEqual(summary.attr_count, 2)
        self.assertEqual(summary.geom_count, 2)
        self.assertIsNone(summary.attr_report)
        self.assertIsNone(summary.geom_report)


if __name__ == "__main__":
    unittest.main()
