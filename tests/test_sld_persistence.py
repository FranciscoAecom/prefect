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
            "pnt_pcd_enov_bbox_brasil_20260514",
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
        self.assertIn("<Name>pnt_pcd_enov_bbox_brasil_20260514</Name>", text)
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
        bbox_style = resolve_layer_sld_style(
            style,
            "pnt_pcd_enov_bbox_brasil_20260514",
        )

        self.assertEqual(main_style["point"]["fill"], "#ef8e03")
        self.assertEqual(bbox_style["point"]["fill"], "#1654ad")

    def test_sld_path_uses_same_stem_as_dataset(self):
        self.assertEqual(
            sld_path_for_dataset(Path("saida") / "pnt_pcd_enov_bbox_brasil_20260514.gpkg"),
            Path("saida") / "pnt_pcd_enov_bbox_brasil_20260514.sld",
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
            dataset_path = Path(temp_dir) / "pnt_pcd_enov_bbox_brasil_20260514.gpkg"
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

            self.assertEqual(paths, [dataset_path.with_suffix(".sld")])
            self.assertTrue(paths[0].exists())
            self.assertIn(
                "<se:Name>pnt_pcd_enov_bbox_brasil_20260514</se:Name>",
                paths[0].read_text(encoding="utf-8"),
            )


if __name__ == "__main__":
    unittest.main()
