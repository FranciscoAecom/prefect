import unittest
from unittest.mock import patch

from core.output.quality import OutputQualitySummary, log_output_quality_summary


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


if __name__ == "__main__":
    unittest.main()
