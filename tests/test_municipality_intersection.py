import unittest
from types import SimpleNamespace
from unittest.mock import patch

import geopandas as gpd
from shapely.geometry import Point, Polygon

from core.processing.context import ProcessingContext
from core.processing.postprocess_step import postprocess_step
from core.spatial.municipality_intersection import assign_municipality_fields_by_intersection


class MunicipalityIntersectionTests(unittest.TestCase):
    def test_assigns_municipality_fields_from_spatial_intersection(self):
        autos = gpd.GeoDataFrame(
            {
                "sdb_cod_munici": ["9999999"],
                "sdb_municipio": ["Nome Incerto"],
                "sdb_uf": ["XX"],
                "geometry": [Point(0.5, 0.5)],
            },
            geometry="geometry",
            crs="EPSG:4326",
        )
        municipalities = gpd.GeoDataFrame(
            {
                "sdb_cd_mun": ["1234567"],
                "sdb_nm_mun": ["Municipio Certo"],
                "sdb_sigla_uf": ["AC"],
                "geometry": [
                    Polygon([(0, 0), (1, 0), (1, 1), (0, 1), (0, 0)]),
                ],
            },
            geometry="geometry",
            crs="EPSG:4326",
        )

        result = assign_municipality_fields_by_intersection(autos, municipalities)

        self.assertEqual(result.loc[0, "acm_cod_munici"], "1234567")
        self.assertEqual(result.loc[0, "acm_municipio"], "Municipio Certo")
        self.assertEqual(result.loc[0, "acm_uf"], "AC")

    @patch("core.processing.postprocess_functions.enrich_with_municipality_intersection")
    def test_postprocess_enriches_auto_infracoes_with_municipalities(self, mock_enrich):
        gdf = gpd.GeoDataFrame(
            {"geometry": [Point(0, 0)]},
            geometry="geometry",
            crs="EPSG:4326",
        )
        enriched = gdf.copy()
        enriched["acm_cod_munici"] = ["1234567"]
        mock_enrich.return_value = enriched
        context = ProcessingContext(
            record=SimpleNamespace(theme_folder="autos_infracao"),
            output_dir="tests/_tmp_output",
            project_config={"project_name": "auto_infracoes"},
            rule_profile_name="auto_infracoes/autos_infracao",
            rule_profile={
                "postprocess_functions": ["enrich_with_municipality_intersection"],
            },
            optional_functions={},
            final_gdf=gdf,
        )

        result = postprocess_step(context)

        mock_enrich.assert_called_once()
        self.assertIn("acm_cod_munici", result.final_gdf.columns)


if __name__ == "__main__":
    unittest.main()
