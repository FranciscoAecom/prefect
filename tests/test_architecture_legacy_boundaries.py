import unittest
from pathlib import Path


class ArchitectureLegacyBoundaryTests(unittest.TestCase):
    LEGACY_TREATMENT_NAME = "pipe" + "line"
    LEGACY_RECORD_NAME = "qu" + "eue"

    def test_root_compatibility_facades_have_been_removed(self):
        facade_paths = [
            Path("core/batch_processor.py"),
            Path("core/dataset_io.py"),
            Path("core/execution_context.py"),
            Path("core/geometry_repair.py"),
            Path("core/helper_unique_values.py"),
            Path("core/naming.py"),
            Path("core") / f"{self.LEGACY_TREATMENT_NAME}.py",
            Path("core") / f"{self.LEGACY_TREATMENT_NAME}_operations.py",
            Path("core/processing_service.py"),
            Path("core/processing_steps.py"),
            Path("core/processing_events.py"),
            Path("core/processing_errors.py"),
            Path("core/record_processor.py"),
            Path("core") / f"{self.LEGACY_RECORD_NAME}_runner.py",
            Path("core/rule_runtime.py"),
            Path("core/schema.py"),
            Path("core/output_manager.py"),
            Path("core/output_paths.py"),
            Path("core/output_quality.py"),
            Path("core/output_writer.py"),
            Path("core/input_preparation.py"),
        ]

        existing_facades = [str(path) for path in facade_paths if path.exists()]

        self.assertEqual(existing_facades, [])

    def test_runtime_code_uses_current_modules_instead_of_removed_root_facades(self):
        offenders = self._files_containing(
            Path("core"),
            "*.py",
            [
                "from core.batch_processor import",
                "from core.dataset_io import",
                "from core.execution_context import",
                "from core.geometry_repair import",
                "from core.helper_unique_values import",
                "from core.naming import",
                f"from core.{self.LEGACY_TREATMENT_NAME} import",
                f"from core.{self.LEGACY_TREATMENT_NAME}_operations import",
                f"from core.{self.LEGACY_RECORD_NAME}_runner import",
                "from core.record_processor import",
                "from core.processing_service import",
                "from core.processing_steps import",
                "from core.processing_events import",
                "from core.processing_errors import",
                "from core.rule_runtime import",
                "from core.schema import",
                "from core.output_manager import",
                "from core.output_paths import",
                "from core.output_quality import",
                "from core.output_writer import",
                "from core.input_preparation import",
            ],
        )

        self.assertEqual(offenders, [])

    def test_legacy_treatment_shims_have_been_removed(self):
        shim_paths = [
            Path("core/flow") / f"{self.LEGACY_TREATMENT_NAME}.py",
            Path("core/tasks") / f"{self.LEGACY_TREATMENT_NAME}.py",
            Path("core/tasks/tasks.py"),
        ]

        existing_shims = [str(path) for path in shim_paths if path.exists()]

        self.assertEqual(existing_shims, [])

    def test_runtime_code_uses_treatment_modules_instead_of_legacy_imports(self):
        offenders = self._files_containing(
            Path("core"),
            "*.py",
            [
                f"from core.flow.{self.LEGACY_TREATMENT_NAME}",
                f"import core.flow.{self.LEGACY_TREATMENT_NAME}",
                f"from core.tasks.{self.LEGACY_TREATMENT_NAME}",
                f"import core.tasks.{self.LEGACY_TREATMENT_NAME}",
                f"data_{self.LEGACY_TREATMENT_NAME}_flow",
            ],
        )

        self.assertEqual(offenders, [])

    def test_treatment_steps_do_not_use_legacy_module_names(self):
        forbidden_paths = [
            Path("core/treatment/steps") / f"{self.LEGACY_TREATMENT_NAME}_step.py",
            Path("core/treatment/steps") / f"mandatory_{self.LEGACY_TREATMENT_NAME}.py",
        ]
        existing_paths = [str(path) for path in forbidden_paths if path.exists()]

        self.assertEqual(existing_paths, [])

        offenders = self._files_containing(
            Path("core/treatment"),
            "*.py",
            [
                f"core.treatment.steps.{self.LEGACY_TREATMENT_NAME}_step",
                f"core.treatment.steps.mandatory_{self.LEGACY_TREATMENT_NAME}",
            ],
        )

        self.assertEqual(offenders, [])

    def test_processing_and_record_compatibility_packages_have_been_removed(self):
        self.assertFalse(Path("core/processing").exists())
        self.assertFalse((Path("core") / self.LEGACY_RECORD_NAME).exists())

    def test_runtime_code_does_not_import_core_record_compatibility_package(self):
        offenders = []
        forbidden_terms = [
            f"from core.{self.LEGACY_RECORD_NAME}",
            f"import core.{self.LEGACY_RECORD_NAME}",
        ]
        for path in Path("core").rglob("*.py"):
            text = path.read_text(encoding="utf-8")
            if any(term in text for term in forbidden_terms):
                offenders.append(str(path))

        self.assertEqual(offenders, [])

    def test_runtime_code_uses_treatment_names_instead_of_processing_facades(self):
        offenders = []
        forbidden_terms = ["from core.processing", "import core.processing"]
        for path in Path("core").rglob("*.py"):
            text = path.read_text(encoding="utf-8")
            if any(term in text for term in forbidden_terms):
                offenders.append(str(path))

        self.assertEqual(offenders, [])

    def test_runtime_code_uses_treatment_status_names(self):
        offenders = []
        forbidden_terms = [
            "INGEST_PROCESSING_STATUSES",
            "processing_statuses_display",
            "can_attempt_processing",
            "processing_" + self.LEGACY_RECORD_NAME,
        ]
        for path in Path("core").rglob("*.py"):
            text = path.read_text(encoding="utf-8")
            if any(term in text for term in forbidden_terms):
                offenders.append(str(path))

        self.assertEqual(offenders, [])

    def test_download_code_uses_treatment_step_names(self):
        offenders = self._files_containing(
            Path("core"),
            "*.py",
            [
                "process_after_download",
                "publish_after_process",
            ],
        )

        self.assertEqual(offenders, [])

    def test_prefect_support_uses_treatment_block_names(self):
        offenders = self._files_containing(
            Path("core/prefect_support"),
            "*.py",
            [
                "DataPipelinePaths",
                "DataPipelineEndpoints",
                f"load_data_{self.LEGACY_TREATMENT_NAME}_paths",
                f"load_data_{self.LEGACY_TREATMENT_NAME}_endpoints",
            ],
        )

        self.assertEqual(offenders, [])

    def test_runtime_code_does_not_include_raster_support(self):
        self.assertFalse(Path("core/raster").exists())
        self.assertFalse(Path("core/treatment/handlers/raster.py").exists())

        offenders = self._files_containing(
            Path("core"),
            "*.py",
            [
                "core.raster",
                "osgeo",
                "GDAL",
                ".tif",
                ".tiff",
                "DATASET_KIND_RASTER",
            ],
        )

        self.assertEqual(offenders, [])

    def test_treatment_uses_direct_record_processor_without_dataset_dispatch(self):
        removed_paths = [
            Path("core/ingest/dataset_types.py"),
            Path("core/treatment/dispatcher.py"),
            Path("core/treatment/handlers"),
        ]

        self.assertEqual([str(path) for path in removed_paths if path.exists()], [])

        offenders = self._files_containing(
            Path("core"),
            "*.py",
            [
                "dataset_kind",
                "dataset_types",
                "process_treatment_record_by_dataset_kind",
                "core.treatment.dispatcher",
                "core.treatment.handlers",
            ],
        )

        self.assertEqual(offenders, [])

    def _files_containing(self, root, pattern, forbidden_terms):
        offenders = []
        for path in root.rglob(pattern):
            text = path.read_text(encoding="utf-8")
            if any(term in text for term in forbidden_terms):
                offenders.append(str(path))
        return offenders


if __name__ == "__main__":
    unittest.main()
