import unittest
import warnings
from unittest.mock import patch


class DeprecatedTreatmentAliasesTests(unittest.TestCase):
    def test_load_processing_queue_warns(self):
        from core.ingest.loader import load_processing_queue

        with patch("core.ingest.loader.load_treatment_queue", return_value=([], [], {})):
            with warnings.catch_warnings(record=True) as caught:
                warnings.simplefilter("always")
                result = load_processing_queue()

        self.assertEqual(result, ([], [], {}))
        self.assertTrue(any(item.category is DeprecationWarning for item in caught))

    def test_prepare_processing_queue_warns(self):
        with warnings.catch_warnings(record=True) as caught:
            warnings.simplefilter("always")
            with patch("core.queue.queue_loader.prepare_treatment_queue", return_value="ctx"):
                from core.queue.queue_loader import prepare_processing_queue

                result = prepare_processing_queue("out")

        self.assertEqual(result, "ctx")
        self.assertTrue(any(item.category is DeprecationWarning for item in caught))

    def test_run_processing_queue_warns(self):
        with warnings.catch_warnings(record=True) as caught:
            warnings.simplefilter("always")
            with patch("core.queue.runner.run_treatment_queue", return_value="done"):
                from core.queue.runner import run_processing_queue

                result = run_processing_queue()

        self.assertEqual(result, "done")
        self.assertTrue(any(item.category is DeprecationWarning for item in caught))

    def test_core_queue_package_exports_legacy_record_runner(self):
        with warnings.catch_warnings(record=True) as caught:
            warnings.simplefilter("always")
            from core.queue import run_queue_record

        self.assertTrue(callable(run_queue_record))
        self.assertTrue(any(item.category is DeprecationWarning for item in caught))

    def test_processing_result_alias_warns(self):
        with warnings.catch_warnings(record=True) as caught:
            warnings.simplefilter("always")
            from core.processing.result import ProcessRecordResult, failure_result

            result = failure_result()

        self.assertEqual(result, ProcessRecordResult(0, None, None))
        self.assertTrue(any(item.category is DeprecationWarning for item in caught))

    def test_processing_context_factory_alias_warns(self):
        with warnings.catch_warnings(record=True) as caught:
            warnings.simplefilter("always")
            from core.processing.context_factory import build_processing_context

        self.assertTrue(callable(build_processing_context))
        self.assertTrue(any(item.category is DeprecationWarning for item in caught))

    def test_processing_pipeline_runner_alias_warns(self):
        with warnings.catch_warnings(record=True) as caught:
            warnings.simplefilter("always")
            from core.processing.pipeline_runner import run_processing_pipeline

        self.assertTrue(callable(run_processing_pipeline))
        self.assertTrue(any(item.category is DeprecationWarning for item in caught))

    def test_processing_record_processor_alias_warns(self):
        with warnings.catch_warnings(record=True) as caught:
            warnings.simplefilter("always")
            from core.processing.record_processor import process_record

        self.assertTrue(callable(process_record))
        self.assertTrue(any(item.category is DeprecationWarning for item in caught))

    def test_ingest_processing_statuses_display_alias_warns(self):
        from core.ingest.run_request import IngestRunRequest

        request = IngestRunRequest()

        with warnings.catch_warnings(record=True) as caught:
            warnings.simplefilter("always")
            result = request.processing_statuses_display()

        self.assertEqual(result, request.treatment_statuses_display())
        self.assertTrue(any(item.category is DeprecationWarning for item in caught))

    def test_ingest_settings_processing_statuses_alias_warns(self):
        from core.config.settings import IngestSettings

        settings = IngestSettings()

        with warnings.catch_warnings(record=True) as caught:
            warnings.simplefilter("always")
            result = settings.processing_statuses

        self.assertEqual(result, settings.treatment_statuses)
        self.assertTrue(any(item.category is DeprecationWarning for item in caught))


if __name__ == "__main__":
    unittest.main()
