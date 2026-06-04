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
        from core.queue.queue_loader import prepare_processing_queue

        with patch("core.queue.queue_loader.prepare_treatment_queue", return_value="ctx"):
            with warnings.catch_warnings(record=True) as caught:
                warnings.simplefilter("always")
                result = prepare_processing_queue("out")

        self.assertEqual(result, "ctx")
        self.assertTrue(any(item.category is DeprecationWarning for item in caught))

    def test_run_processing_queue_warns(self):
        from core.queue.runner import run_processing_queue

        with patch("core.queue.runner.run_treatment_queue", return_value="done"):
            with warnings.catch_warnings(record=True) as caught:
                warnings.simplefilter("always")
                result = run_processing_queue()

        self.assertEqual(result, "done")
        self.assertTrue(any(item.category is DeprecationWarning for item in caught))


if __name__ == "__main__":
    unittest.main()
