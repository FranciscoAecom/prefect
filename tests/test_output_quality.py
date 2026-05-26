import unittest
from unittest.mock import patch

import geopandas as gpd
from shapely.geometry import Point

from core.reporting.constants import DUPLICATE_RECORD_FLAG_FIELD
from core.reporting.duplicate_reports import export_duplicate_reports
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

    @patch("core.output.quality.export_duplicate_reports")
    def test_profile_can_disable_selected_quality_outputs(self, mock_export):
        gdf = gpd.GeoDataFrame(
            {
                "sdb_codigo": ["A", "A"],
                "geometry": [Point(0, 0), Point(0, 0)],
            },
            geometry="geometry",
            crs="EPSG:4326",
        )

        summary = build_output_quality_summary(
            gdf,
            ".",
            "pnt_teste",
            rule_profile={
                "quality_outputs": {
                    "attribute_duplicates": False,
                    "geometric_duplicates": False,
                    "ogc_invalid_geometries": False,
                }
            },
        )

        mock_export.assert_not_called()
        self.assertEqual(summary.attr_count, 0)
        self.assertEqual(summary.geom_count, 0)
        self.assertEqual(summary.ogc_invalid_count, 0)
        self.assertFalse(summary.config.attribute_duplicates)
        self.assertFalse(summary.config.geometric_duplicates)
        self.assertFalse(summary.config.ogc_invalid_geometries)

    @patch("core.output.quality.export_duplicate_reports")
    def test_profile_can_disable_full_record_duplicate_flag(self, mock_export):
        mock_export.return_value = ("attr.xlsx", "geom.gpkg", None, 2, 2, 0, {})
        gdf = gpd.GeoDataFrame(
            {
                "sdb_codigo": ["A", "A"],
                "geometry": [Point(0, 0), Point(0, 0)],
            },
            geometry="geometry",
            crs="EPSG:4326",
        )

        build_output_quality_summary(
            gdf,
            ".",
            "pnt_teste",
            rule_profile={
                "quality_outputs": {
                    "full_record_duplicate_flag": False,
                }
            },
        )

        self.assertFalse(
            mock_export.call_args.kwargs["include_full_record_duplicate_flag"]
        )

    @patch("core.reporting.duplicate_reports._save_tabular_report", return_value="attr.xlsx")
    @patch("core.reporting.duplicate_reports._save_geospatial_report", return_value="geom.gpkg")
    def test_geometric_duplicate_report_flags_full_record_duplicates_without_identifier(
        self,
        mock_save_geospatial_report,
        _mock_save_tabular_report,
    ):
        gdf = gpd.GeoDataFrame(
            {
                "acm_id": [1, 2, 3],
                "sdb_codigo": ["A", "A", "B"],
                "sdb_nome": ["Mesmo", "Mesmo", "Mesmo"],
                "geometry": [Point(0, 0), Point(0, 0), Point(0, 0)],
            },
            geometry="geometry",
            crs="EPSG:4326",
        )
        attr_duplicates = gdf.iloc[[0, 1]].copy()
        geom_duplicates = gdf.copy()

        export_duplicate_reports(
            gdf,
            ".",
            "pnt_teste",
            attr_duplicates=attr_duplicates,
            attr_count=2,
            geom_duplicates=geom_duplicates,
            geom_count=3,
            ogc_invalid=None,
            ogc_invalid_count=0,
            ogc_error_summary={},
        )

        exported_geom_duplicates = mock_save_geospatial_report.call_args.args[1]
        self.assertEqual(
            exported_geom_duplicates[DUPLICATE_RECORD_FLAG_FIELD].tolist(),
            [True, True, False],
        )

    @patch("core.reporting.duplicate_reports._save_tabular_report", return_value="attr.xlsx")
    @patch("core.reporting.duplicate_reports._save_geospatial_report", return_value="geom.gpkg")
    def test_geometric_duplicate_report_can_skip_full_record_flag(
        self,
        mock_save_geospatial_report,
        _mock_save_tabular_report,
    ):
        gdf = gpd.GeoDataFrame(
            {
                "acm_id": [1, 2],
                "sdb_codigo": ["A", "A"],
                "geometry": [Point(0, 0), Point(0, 0)],
            },
            geometry="geometry",
            crs="EPSG:4326",
        )

        export_duplicate_reports(
            gdf,
            ".",
            "pnt_teste",
            attr_duplicates=gdf.copy(),
            attr_count=2,
            geom_duplicates=gdf.copy(),
            geom_count=2,
            ogc_invalid=None,
            ogc_invalid_count=0,
            ogc_error_summary={},
            include_full_record_duplicate_flag=False,
        )

        exported_geom_duplicates = mock_save_geospatial_report.call_args.args[1]
        self.assertNotIn(DUPLICATE_RECORD_FLAG_FIELD, exported_geom_duplicates.columns)


if __name__ == "__main__":
    unittest.main()
