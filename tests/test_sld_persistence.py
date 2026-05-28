import json
import tempfile
import unittest
from pathlib import Path

import geopandas as gpd
from shapely.geometry import Point, Polygon

from core.sld.persistence import (
    build_sld_style,
    detect_geometry_kind,
    persist_stage_slds,
    render_sld,
    resolve_layer_sld_style,
    sld_path_for_dataset,
)


class SldPersistenceTests(unittest.TestCase):
    def test_render_point_sld_version_1_0(self):
        text = render_sld(
            "pnt_pcd_enov_20260514",
            "point",
            {
                "version": "1.0.0",
                "rule_name": "Single symbol",
                "point": {
                    "well_known_name": "circle",
                    "fill": "#1654ad",
                    "stroke": "#232323",
                    "stroke_width": "0.5",
                    "size": "7",
                },
                "line": {},
                "polygon": {},
            },
        )

        self.assertIn('version="1.0.0"', text)
        self.assertIn("<Name>pnt_pcd_enov_20260514</Name>", text)
        self.assertIn("<PointSymbolizer>", text)
        self.assertIn('<CssParameter name="fill">#1654ad</CssParameter>', text)

    def test_render_point_sld_version_1_1(self):
        text = render_sld(
            "pnt_pcd_enov_20260514",
            "point",
            {
                "version": "1.1.0",
                "rule_name": "Single symbol",
                "point": {
                    "well_known_name": "circle",
                    "fill": "#ef8e03",
                    "stroke": "#232323",
                    "stroke_width": "0.5",
                    "size": "7",
                },
                "line": {},
                "polygon": {},
            },
        )

        self.assertIn('version="1.1.0"', text)
        self.assertIn("<se:Name>pnt_pcd_enov_20260514</se:Name>", text)
        self.assertIn("<se:PointSymbolizer>", text)
        self.assertIn('<se:SvgParameter name="fill">#ef8e03</se:SvgParameter>', text)

    def test_resolve_layer_sld_style_overrides_specific_layer(self):
        style = build_sld_style(
            {
                "sld": {
                    "version": "1.1.0",
                    "point": {"fill": "#1654ad"},
                    "layers": {
                        "pnt_pcd_enov_20260514": {
                            "point": {"fill": "#ef8e03"}
                        }
                    },
                }
            }
        )

        main_style = resolve_layer_sld_style(style, "pnt_pcd_enov_20260514")
        fallback_style = resolve_layer_sld_style(
            style,
            "pnt_pcd_outro_20260514",
        )

        self.assertEqual(main_style["point"]["fill"], "#ef8e03")
        self.assertEqual(fallback_style["point"]["fill"], "#1654ad")

    def test_render_categorized_polygon_sld_version_1_1(self):
        style = build_sld_style(
            {
                "sld": {
                    "version": "1.1.0",
                    "layers": {
                        "pol_pcd_ur_car_ac_20260514": {
                            "rules": [
                                {
                                    "name": "Area de Uso Restrito para declividade de 25 a 45 graus",
                                    "title": "Area de Uso Restrito para declividade de 25 a 45 graus",
                                    "filter": {
                                        "property": "sdb_nom_tema",
                                        "literal": "Area de Uso Restrito para declividade de 25 a 45 graus",
                                    },
                                    "polygon": {
                                        "fill": "#087d03",
                                    },
                                },
                                {
                                    "name": "Area de Uso Restrito para regioes pantaneiras",
                                    "title": "Area de Uso Restrito para regioes pantaneiras",
                                    "filter": {
                                        "property": "sdb_nom_tema",
                                        "literal": "Area de Uso Restrito para regioes pantaneiras",
                                    },
                                    "polygon": {
                                        "fill": "#4fd84a",
                                    },
                                },
                            ]
                        }
                    },
                }
            }
        )
        layer_style = resolve_layer_sld_style(style, "pol_pcd_ur_car_ac_20260514")

        text = render_sld("pol_pcd_ur_car_ac_20260514", "polygon", layer_style)

        self.assertIn("<se:Name>pol_pcd_ur_car_ac_20260514</se:Name>", text)
        self.assertIn("<se:Rule>", text)
        self.assertIn("<ogc:PropertyName>sdb_nom_tema</ogc:PropertyName>", text)
        self.assertIn(
            "<ogc:Literal>Area de Uso Restrito para declividade de 25 a 45 graus</ogc:Literal>",
            text,
        )
        self.assertIn('<se:SvgParameter name="fill">#087d03</se:SvgParameter>', text)
        self.assertIn('<se:SvgParameter name="fill">#4fd84a</se:SvgParameter>', text)

    def test_localidades_style_categorizes_ct_localidade(self):
        style_path = Path("rules/localidades/localidades/style.json")
        style = build_sld_style(json.loads(style_path.read_text(encoding="utf-8")))
        text = render_sld("pol_loc_loc_20251119", "point", style)

        self.assertEqual(len(style["rules"]), 12)
        self.assertEqual(
            {rule["filter"]["property"] for rule in style["rules"]},
            {"sdb_ct_localidade"},
        )
        self.assertIn("<ogc:PropertyName>sdb_ct_localidade</ogc:PropertyName>", text)
        self.assertIn("<ogc:Literal>Cidade</ogc:Literal>", text)
        self.assertIn('<se:SvgParameter name="fill">#1654AD</se:SvgParameter>', text)

    def test_setor_censitario_style_matches_single_symbol_polygon_model(self):
        style_path = Path("rules/setor_censitario/setor_censitario/style.json")
        style = build_sld_style(json.loads(style_path.read_text(encoding="utf-8")))
        text = render_sld("pol_loc_cse_20241114", "polygon", style)

        self.assertIn('version="1.1.0"', text)
        self.assertIn("<se:Name>pol_loc_cse_20241114</se:Name>", text)
        self.assertIn("<se:Name>Single symbol</se:Name>", text)
        self.assertIn('<se:SvgParameter name="fill">#ef8e03</se:SvgParameter>', text)
        self.assertIn('<se:SvgParameter name="stroke">#232323</se:SvgParameter>', text)
        self.assertIn('<se:SvgParameter name="stroke-width">1</se:SvgParameter>', text)
        self.assertIn(
            '<se:SvgParameter name="stroke-linejoin">bevel</se:SvgParameter>',
            text,
        )

    def test_sld_path_uses_same_stem_as_dataset(self):
        self.assertEqual(
            sld_path_for_dataset(Path("saida") / "pnt_pcd_enov_20260514.gpkg"),
            Path("saida") / "sld_pnt_pcd_enov_20260514.sld",
        )

    def test_detect_geometry_kind(self):
        point_gdf = gpd.GeoDataFrame(
            {"geometry": [Point(0, 0)]},
            geometry="geometry",
            crs="EPSG:4326",
        )
        polygon_gdf = gpd.GeoDataFrame(
            {"geometry": [Polygon([(0, 0), (1, 0), (1, 1), (0, 0)])]},
            geometry="geometry",
            crs="EPSG:4326",
        )

        self.assertEqual(detect_geometry_kind(point_gdf), "point")
        self.assertEqual(detect_geometry_kind(polygon_gdf), "polygon")

    def test_persist_stage_slds_writes_file_next_to_dataset(self):
        gdf = gpd.GeoDataFrame(
            {"geometry": [Point(0, 0)]},
            geometry="geometry",
            crs="EPSG:4326",
        )
        with tempfile.TemporaryDirectory() as temp_dir:
            dataset_path = Path(temp_dir) / "pnt_pcd_enov_20260514.gpkg"
            paths = persist_stage_slds(
                [{"path": dataset_path, "gdf": gdf}],
                rule_profile={
                    "sld": {
                        "version": "1.1.0",
                        "point": {
                            "fill": "#1654ad",
                            "stroke": "#232323",
                            "stroke_width": "0.5",
                            "size": "7",
                        }
                    }
                },
            )

            self.assertEqual(
                paths,
                [dataset_path.parent / "sld_pnt_pcd_enov_20260514.sld"],
            )
            self.assertTrue(paths[0].exists())
            self.assertIn(
                "<se:Name>pnt_pcd_enov_20260514</se:Name>",
                paths[0].read_text(encoding="utf-8"),
            )


if __name__ == "__main__":
    unittest.main()
