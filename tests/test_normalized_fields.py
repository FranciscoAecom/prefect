import unittest

import geopandas as gpd
import pandas as pd
from shapely.geometry import Point

from core.validation.domain_validation import validate_shapefile_attribute
from core.validation.normalized_fields import (
    apply_normalized_column_if_changed,
    fill_missing_normalized_columns,
    is_normalized_column,
    is_source_column,
    normalized_column_name,
    series_has_normalized_changes,
)


class NormalizedFieldsTests(unittest.TestCase):
    def test_derives_acm_name_from_sdb_source_column(self):
        self.assertTrue(is_source_column("sdb_nm_rgi"))
        self.assertEqual(normalized_column_name("sdb_nm_rgi"), "acm_nm_rgi")

    def test_preserves_existing_acm_name(self):
        self.assertTrue(is_normalized_column("acm_nm_rgi"))
        self.assertEqual(normalized_column_name("acm_nm_rgi"), "acm_nm_rgi")

    def test_prefixes_non_sdb_columns_predictably(self):
        self.assertEqual(normalized_column_name("nome"), "acm_nome")

    def test_detects_series_changes_with_nulls(self):
        source = pd.Series(["A", None])
        same = pd.Series(["A", None])
        changed = pd.Series(["B", None])

        self.assertFalse(series_has_normalized_changes(source, same))
        self.assertTrue(series_has_normalized_changes(source, changed))

    def test_apply_normalized_column_preserves_original_source(self):
        gdf = gpd.GeoDataFrame(
            {"sdb_nm_rgi": ["Ilheus"], "geometry": [Point(0, 0)]},
            geometry="geometry",
            crs="EPSG:4326",
        )

        result = apply_normalized_column_if_changed(
            gdf,
            "sdb_nm_rgi",
            pd.Series(["Ilheus - Itabuna"]),
        )

        self.assertEqual(result.loc[0, "sdb_nm_rgi"], "Ilheus")
        self.assertEqual(result.loc[0, "acm_nm_rgi"], "Ilheus - Itabuna")

    def test_domain_validation_uses_contract_and_preserves_source(self):
        gdf = gpd.GeoDataFrame(
            {"sdb_nm_rgi": ["Ilheus"], "geometry": [Point(0, 0)]},
            geometry="geometry",
            crs="EPSG:4326",
        )
        profile = {
            "fields": {
                "sdb_nm_rgi": {
                    "accepted_values": ["Ilheus - Itabuna"],
                    "aliases": {"Ilheus": "Ilheus - Itabuna"},
                }
            }
        }

        result = validate_shapefile_attribute(
            gdf,
            "sdb_nm_rgi",
            rule_profile=profile,
        )

        self.assertEqual(result.loc[0, "sdb_nm_rgi"], "Ilheus")
        self.assertEqual(result.loc[0, "acm_nm_rgi"], "Ilheus - Itabuna")

    def test_fills_missing_normalized_values_after_batch_concat(self):
        gdf = gpd.GeoDataFrame(
            {
                "sdb_nm_rgi": ["Cacoal", "Goiana - Timbauba"],
                "acm_nm_rgi": [pd.NA, "Goiana - Timbauba"],
                "geometry": [Point(0, 0), Point(1, 1)],
            },
            geometry="geometry",
            crs="EPSG:4326",
        )

        result = fill_missing_normalized_columns(gdf)

        self.assertEqual(
            result["acm_nm_rgi"].tolist(),
            ["Cacoal", "Goiana - Timbauba"],
        )


if __name__ == "__main__":
    unittest.main()
