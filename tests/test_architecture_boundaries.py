import unittest
from pathlib import Path


class ArchitectureBoundaryTests(unittest.TestCase):
    def test_car_projects_use_single_shared_optional_functions_module(self):
        from projects.functions.car_common import CAR_PROJECT_OPERATIONS
        from projects.registry import PROJECT_FUNCTION_MODULES

        self.assertEqual(
            PROJECT_FUNCTION_MODULES,
            dict.fromkeys(CAR_PROJECT_OPERATIONS, "car_common"),
        )
        legacy_modules = [
            Path("projects/functions") / f"{project_name}.py"
            for project_name in CAR_PROJECT_OPERATIONS
        ]
        self.assertEqual([str(path) for path in legacy_modules if path.exists()], [])

    def test_ogc_coordinates_does_not_depend_on_persistence(self):
        text = Path("core/spatial/ogc_coordinates.py").read_text(encoding="utf-8")

        self.assertNotIn("persistence", text)

    def test_metadata_dictionary_does_not_depend_on_xml_templates(self):
        text = Path("core/metadata/dictionary.py").read_text(encoding="utf-8")

        self.assertNotIn("template", text.lower())

    def test_tabular_validation_modules_do_not_import_rule_layer(self):
        offenders = self._files_containing(
            Path("core/validation"),
            "tabular_*.py",
            ["core.rules", "core.validation.rule_"],
        )

        self.assertEqual(offenders, [])

    def test_rules_package_does_not_import_geopandas(self):
        offenders = self._files_containing(
            Path("core/rules"),
            "*.py",
            ["geopandas"],
        )

        self.assertEqual(offenders, [])

    def test_output_paths_does_not_import_geopandas(self):
        text = Path("core/output/paths.py").read_text(encoding="utf-8")

        self.assertNotIn("geopandas", text)

    def test_output_quality_does_not_write_gpkg_directly(self):
        text = Path("core/output/quality.py").read_text(encoding="utf-8")

        self.assertNotIn("write_output_gpkg", text)

    def test_legacy_rule_modules_have_been_removed(self):
        offenders = list(Path("core/validation").glob("rule_*.py"))
        offenders.extend(Path("core/validation").glob("domain_rules.py"))

        self.assertEqual([str(path) for path in offenders], [])

    def test_root_compatibility_facades_have_been_removed(self):
        facade_paths = [
            Path("core/batch_processor.py"),
            Path("core/dataset_io.py"),
            Path("core/execution_context.py"),
            Path("core/geometry_repair.py"),
            Path("core/helper_unique_values.py"),
            Path("core/naming.py"),
            Path("core/pipeline.py"),
            Path("core/pipeline_operations.py"),
            Path("core/processing_service.py"),
            Path("core/processing_steps.py"),
            Path("core/processing_events.py"),
            Path("core/processing_errors.py"),
            Path("core/record_processor.py"),
            Path("core/queue_runner.py"),
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
                "from core.pipeline import",
                "from core.pipeline_operations import",
                "from core.queue_runner import",
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

    def test_legacy_pipeline_treatment_shims_have_been_removed(self):
        shim_paths = [
            Path("core/flow/pipeline.py"),
            Path("core/tasks/pipeline.py"),
            Path("core/tasks/tasks.py"),
        ]

        existing_shims = [str(path) for path in shim_paths if path.exists()]

        self.assertEqual(existing_shims, [])

    def test_runtime_code_uses_treatment_modules_instead_of_legacy_pipeline_imports(self):
        offenders = self._files_containing(
            Path("core"),
            "*.py",
            [
                "from core.flow.pipeline",
                "import core.flow.pipeline",
                "from core.tasks.pipeline",
                "import core.tasks.pipeline",
                "data_pipeline_flow",
            ],
        )

        self.assertEqual(offenders, [])

    def test_processing_and_queue_compatibility_packages_have_been_removed(self):
        self.assertFalse(Path("core/processing").exists())
        self.assertFalse(Path("core/queue").exists())

    def test_runtime_code_does_not_import_core_queue_compatibility_package(self):
        offenders = []
        forbidden_terms = ["from core.queue", "import core.queue"]
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
            "processing_queue",
        ]
        for path in Path("core").rglob("*.py"):
            text = path.read_text(encoding="utf-8")
            if any(term in text for term in forbidden_terms):
                offenders.append(str(path))

        self.assertEqual(offenders, [])

    def test_prefect_decorators_stay_in_flow_and_tasks_packages(self):
        allowed_roots = {Path("core/flow"), Path("core/tasks")}
        offenders = []

        for path in Path("core").rglob("*.py"):
            text = path.read_text(encoding="utf-8")
            if "@flow(" not in text and "@task(" not in text:
                continue
            if not any(path.is_relative_to(root) for root in allowed_roots):
                offenders.append(str(path))

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
