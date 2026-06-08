import unittest
from pathlib import Path
from types import SimpleNamespace

from core.versioning.paths import (
    contains_geographic_dataset,
    normalize_date_folder,
    normalize_version_folder,
    resolve_dataset_version_plan,
    resolve_next_available_version,
)


def _record(**overrides):
    values = {
        "status": "treatment",
        "access_constraints": "restricted",
        "category_acronym": "pcd",
        "theme_folder": "autos_infracao",
        "citation": "IBAMA",
        "date": "2021-09-15",
    }
    values.update(overrides)
    return SimpleNamespace(**values)


class VersioningPathsTests(unittest.TestCase):
    def test_normalizes_date_and_version_folders(self):
        self.assertEqual(normalize_date_folder("2021-09-15"), "20210915")
        self.assertEqual(normalize_date_folder("20210915"), "20210915")
        self.assertEqual(normalize_version_folder("1"), "01")
        self.assertEqual(normalize_version_folder("02"), "02")

    def test_resolves_initial_temp_bronze_silver_paths(self):
        base = Path("L:/base")
        plan = resolve_dataset_version_plan(_record(), base_path=base, create=False)

        expected_tail = Path("restricted") / "pcd" / "autos_infracao" / "IBAMA" / "20210915" / "00"
        self.assertEqual(plan.version, "00")
        self.assertEqual(plan.temp_dir, base / "temp" / expected_tail)
        self.assertEqual(plan.bronze_dir, base / "bronze_data" / expected_tail)
        self.assertEqual(plan.silver_dir, base / "silver_data" / expected_tail)

    def test_schedule_status_resolves_temp_bronze_silver_paths(self):
        base = Path("L:/base")
        plan = resolve_dataset_version_plan(
            _record(status="schedule 2026-06-08 18:10"),
            base_path=base,
            create=False,
        )

        expected_tail = (
            Path("restricted")
            / "pcd"
            / "autos_infracao"
            / "IBAMA"
            / "20210915"
            / "00"
        )
        self.assertEqual(plan.version, "00")
        self.assertEqual(plan.temp_dir, base / "temp" / expected_tail)
        self.assertEqual(plan.bronze_dir, base / "bronze_data" / expected_tail)
        self.assertEqual(plan.silver_dir, base / "silver_data" / expected_tail)

    def test_schedule_with_treatment_status_resolves_temp_bronze_silver_paths(self):
        base = Path("L:/base")
        plan = resolve_dataset_version_plan(
            _record(status="schedule 2026-06-08 18:10 treatment"),
            base_path=base,
            create=False,
        )

        expected_tail = (
            Path("restricted")
            / "pcd"
            / "autos_infracao"
            / "IBAMA"
            / "20210915"
            / "00"
        )
        self.assertEqual(plan.version, "00")
        self.assertEqual(plan.temp_dir, base / "temp" / expected_tail)
        self.assertEqual(plan.bronze_dir, base / "bronze_data" / expected_tail)
        self.assertEqual(plan.silver_dir, base / "silver_data" / expected_tail)

    def test_treatment_uses_next_version_when_bronze_has_geographic_file(self):
        with self.subTest("gpkg conflict"):
            base = Path("tests") / "_tmp_versioning_gpkg"
            self.addCleanup(lambda: _remove_tree(base))
            conflict = (
                base
                / "bronze_data"
                / "restricted"
                / "pcd"
                / "autos_infracao"
                / "IBAMA"
                / "20210915"
                / "00"
            )
            conflict.mkdir(parents=True)
            (conflict / "bruto.gpkg").write_text("", encoding="utf-8")

            plan = resolve_dataset_version_plan(_record(), base_path=base, create=False)

            self.assertEqual(plan.version, "01")

    def test_existing_version_without_geographic_file_can_be_reused(self):
        base = Path("tests") / "_tmp_versioning_empty"
        self.addCleanup(lambda: _remove_tree(base))
        empty_version = (
            base
            / "bronze_data"
            / "restricted"
            / "pcd"
            / "autos_infracao"
            / "IBAMA"
            / "20210915"
            / "00"
        )
        empty_version.mkdir(parents=True)
        (empty_version / "manifest.json").write_text("{}", encoding="utf-8")

        plan = resolve_dataset_version_plan(_record(), base_path=base, create=False)

        self.assertEqual(plan.version, "00")

    def test_treatment_does_not_reuse_existing_version(self):
        base = Path("tests") / "_tmp_versioning_reprocess"
        self.addCleanup(lambda: _remove_tree(base))
        date_root = (
            base
            / "bronze_data"
            / "restricted"
            / "pcd"
            / "autos_infracao"
            / "IBAMA"
            / "20210915"
        )
        (date_root / "00").mkdir(parents=True)
        (date_root / "02").mkdir(parents=True)

        plan = resolve_dataset_version_plan(_record(), base_path=base, create=False)

        self.assertEqual(plan.version, "00")

    def test_treatment_uses_next_available_version(self):
        base = Path("tests") / "_tmp_versioning_reprocess_latest"
        self.addCleanup(lambda: _remove_tree(base))
        date_root = (
            base
            / "bronze_data"
            / "restricted"
            / "pcd"
            / "autos_infracao"
            / "IBAMA"
            / "20210915"
        )
        (date_root / "00").mkdir(parents=True)
        (date_root / "02").mkdir(parents=True)

        version = resolve_next_available_version(
            date_root,
            status="treatment",
        )

        self.assertEqual(version, "00")

    def test_contains_geographic_dataset_detects_shp_or_gpkg(self):
        base = Path("tests") / "_tmp_versioning_geo"
        self.addCleanup(lambda: _remove_tree(base))
        nested = base / "nested"
        nested.mkdir(parents=True)
        self.assertFalse(contains_geographic_dataset(base))

        (nested / "base.shp").write_text("", encoding="utf-8")

        self.assertTrue(contains_geographic_dataset(base))

    def test_rejects_missing_required_path_fields(self):
        with self.assertRaisesRegex(ValueError, "access_constraints"):
            resolve_dataset_version_plan(
                _record(access_constraints=""),
                base_path=Path("tests") / "_tmp_versioning_invalid",
                create=False,
            )


def _remove_tree(path):
    import shutil

    shutil.rmtree(path, ignore_errors=True)


if __name__ == "__main__":
    unittest.main()
