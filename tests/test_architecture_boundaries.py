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
