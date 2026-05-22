from pathlib import Path
from xml.sax.saxutils import escape

from core.utils import log


DEFAULT_SLD_STYLE = {
    "version": "1.0.0",
    "rule_name": "Single symbol",
    "point": {
        "well_known_name": "circle",
        "fill": "#1654ad",
        "stroke": "#232323",
        "stroke_width": "0.5",
        "size": "7",
    },
    "line": {
        "stroke": "#232323",
        "stroke_width": "0.5",
    },
    "polygon": {
        "fill": "#1654ad",
        "stroke": "#232323",
        "stroke_width": "0.5",
    },
}


def persist_stage_slds(outputs, rule_profile=None, persist_dataset=True):
    if not persist_dataset:
        return []

    base_style = build_sld_style(rule_profile or {})
    sld_paths = []
    for output in outputs:
        output_path = Path(output["path"])
        style = resolve_layer_sld_style(base_style, output_path.stem)
        sld_path = sld_path_for_dataset(output_path)
        sld_text = render_sld(
            layer_name=output_path.stem,
            geometry_kind=detect_geometry_kind(output.get("gdf")),
            style=style,
        )
        sld_path.write_text(sld_text, encoding="utf-8")
        sld_paths.append(sld_path)

    if sld_paths:
        log("Arquivos SLD gerados: " + ", ".join(str(path) for path in sld_paths))
    return sld_paths


def build_sld_style(rule_profile):
    configured = rule_profile.get("sld", {}) if isinstance(rule_profile, dict) else {}
    style = {
        "version": DEFAULT_SLD_STYLE["version"],
        "rule_name": DEFAULT_SLD_STYLE["rule_name"],
        "point": dict(DEFAULT_SLD_STYLE["point"]),
        "line": dict(DEFAULT_SLD_STYLE["line"]),
        "polygon": dict(DEFAULT_SLD_STYLE["polygon"]),
        "layers": {},
    }
    if not isinstance(configured, dict):
        return style

    if isinstance(configured.get("version"), str) and configured["version"].strip():
        style["version"] = configured["version"].strip()

    if isinstance(configured.get("rule_name"), str) and configured["rule_name"].strip():
        style["rule_name"] = configured["rule_name"].strip()

    for section in ("point", "line", "polygon"):
        if isinstance(configured.get(section), dict):
            style[section].update(normalize_style_mapping(configured[section]))

    if isinstance(configured.get("layers"), dict):
        style["layers"] = {
            str(layer_name): normalize_layer_style(layer_style)
            for layer_name, layer_style in configured["layers"].items()
            if isinstance(layer_style, dict)
        }
    return style


def normalize_layer_style(layer_style):
    normalized = {}
    for key in ("version", "rule_name"):
        if isinstance(layer_style.get(key), str) and layer_style[key].strip():
            normalized[key] = layer_style[key].strip()
    for section in ("point", "line", "polygon"):
        if isinstance(layer_style.get(section), dict):
            normalized[section] = normalize_style_mapping(layer_style[section])
    return normalized


def normalize_style_mapping(style_mapping):
    return {
        str(key): str(value)
        for key, value in style_mapping.items()
        if value is not None
    }


def resolve_layer_sld_style(base_style, layer_name):
    style = {
        "version": base_style["version"],
        "rule_name": base_style["rule_name"],
        "point": dict(base_style["point"]),
        "line": dict(base_style["line"]),
        "polygon": dict(base_style["polygon"]),
        "layers": dict(base_style.get("layers", {})),
    }
    layer_style = style["layers"].get(layer_name, {})
    if not isinstance(layer_style, dict):
        return style

    for key in ("version", "rule_name"):
        if key in layer_style:
            style[key] = layer_style[key]
    for section in ("point", "line", "polygon"):
        if isinstance(layer_style.get(section), dict):
            style[section].update(layer_style[section])
    return style


def sld_path_for_dataset(dataset_path):
    return Path(dataset_path).with_suffix(".sld")


def detect_geometry_kind(gdf):
    if gdf is None or "geometry" not in getattr(gdf, "columns", []):
        return "point"

    geometry = gdf.geometry
    valid_geometry = geometry[geometry.notna() & (~geometry.is_empty)]
    if valid_geometry.empty:
        return "point"

    geometry_types = set(valid_geometry.geom_type)
    if any("Polygon" in geometry_type for geometry_type in geometry_types):
        return "polygon"
    if any("LineString" in geometry_type for geometry_type in geometry_types):
        return "line"
    return "point"


def render_sld(layer_name, geometry_kind, style):
    if str(style.get("version", "")).startswith("1.1"):
        return render_sld_1_1(layer_name, geometry_kind, style)
    return render_sld_1_0(layer_name, geometry_kind, style)


def render_sld_1_0(layer_name, geometry_kind, style):
    symbolizer = render_symbolizer(geometry_kind, style)
    return "\n".join(
        [
            '<?xml version="1.0" encoding="UTF-8"?>',
            (
                '<StyledLayerDescriptor xmlns="http://www.opengis.net/sld" '
                f'version="{escape(style["version"])}" xmlns:ogc="http://www.opengis.net/ogc" '
                'xmlns:xlink="http://www.w3.org/1999/xlink" '
                'xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" '
                'xsi:schemaLocation="http://www.opengis.net/sld '
                f'http://schemas.opengis.net/sld/{escape(style["version"])}/StyledLayerDescriptor.xsd">'
            ),
            "  <NamedLayer>",
            f"    <Name>{escape(layer_name)}</Name>",
            "    <UserStyle>",
            f"      <Name>{escape(layer_name)}</Name>",
            "      <FeatureTypeStyle>",
            "        <Rule>",
            f"          <Name>{escape(style['rule_name'])}</Name>",
            symbolizer,
            "        </Rule>",
            "      </FeatureTypeStyle>",
            "    </UserStyle>",
            "  </NamedLayer>",
            "</StyledLayerDescriptor>",
            "",
        ]
    )


def render_sld_1_1(layer_name, geometry_kind, style):
    symbolizer = render_symbolizer_1_1(geometry_kind, style)
    return "\n".join(
        [
            '<?xml version="1.0" encoding="UTF-8"?>',
            (
                '<StyledLayerDescriptor xmlns="http://www.opengis.net/sld" '
                f'version="{escape(style["version"])}" xmlns:ogc="http://www.opengis.net/ogc" '
                'xmlns:xlink="http://www.w3.org/1999/xlink" '
                'xsi:schemaLocation="http://www.opengis.net/sld '
                f'http://schemas.opengis.net/sld/{escape(style["version"])}/StyledLayerDescriptor.xsd" '
                'xmlns:se="http://www.opengis.net/se" '
                'xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">'
            ),
            "  <NamedLayer>",
            f"    <se:Name>{escape(layer_name)}</se:Name>",
            "    <UserStyle>",
            f"      <se:Name>{escape(layer_name)}</se:Name>",
            "      <se:FeatureTypeStyle>",
            "        <se:Rule>",
            f"          <se:Name>{escape(style['rule_name'])}</se:Name>",
            symbolizer,
            "        </se:Rule>",
            "      </se:FeatureTypeStyle>",
            "    </UserStyle>",
            "  </NamedLayer>",
            "</StyledLayerDescriptor>",
            "",
        ]
    )


def render_symbolizer(geometry_kind, style):
    if geometry_kind == "polygon":
        return render_polygon_symbolizer(style["polygon"])
    if geometry_kind == "line":
        return render_line_symbolizer(style["line"])
    return render_point_symbolizer(style["point"])


def render_symbolizer_1_1(geometry_kind, style):
    if geometry_kind == "polygon":
        return render_polygon_symbolizer_1_1(style["polygon"])
    if geometry_kind == "line":
        return render_line_symbolizer_1_1(style["line"])
    return render_point_symbolizer_1_1(style["point"])


def render_point_symbolizer(style):
    return "\n".join(
        [
            "          <PointSymbolizer>",
            "            <Graphic>",
            "              <Mark>",
            f"                <WellKnownName>{escape(style['well_known_name'])}</WellKnownName>",
            "                <Fill>",
            f"                  <CssParameter name=\"fill\">{escape(style['fill'])}</CssParameter>",
            "                </Fill>",
            "                <Stroke>",
            f"                  <CssParameter name=\"stroke\">{escape(style['stroke'])}</CssParameter>",
            f"                  <CssParameter name=\"stroke-width\">{escape(style['stroke_width'])}</CssParameter>",
            "                </Stroke>",
            "              </Mark>",
            f"              <Size>{escape(style['size'])}</Size>",
            "            </Graphic>",
            "          </PointSymbolizer>",
        ]
    )


def render_point_symbolizer_1_1(style):
    return "\n".join(
        [
            "          <se:PointSymbolizer>",
            "            <se:Graphic>",
            "              <se:Mark>",
            f"                <se:WellKnownName>{escape(style['well_known_name'])}</se:WellKnownName>",
            "                <se:Fill>",
            f"                  <se:SvgParameter name=\"fill\">{escape(style['fill'])}</se:SvgParameter>",
            "                </se:Fill>",
            "                <se:Stroke>",
            f"                  <se:SvgParameter name=\"stroke\">{escape(style['stroke'])}</se:SvgParameter>",
            f"                  <se:SvgParameter name=\"stroke-width\">{escape(style['stroke_width'])}</se:SvgParameter>",
            "                </se:Stroke>",
            "              </se:Mark>",
            f"              <se:Size>{escape(style['size'])}</se:Size>",
            "            </se:Graphic>",
            "          </se:PointSymbolizer>",
        ]
    )


def render_line_symbolizer(style):
    return "\n".join(
        [
            "          <LineSymbolizer>",
            "            <Stroke>",
            f"              <CssParameter name=\"stroke\">{escape(style['stroke'])}</CssParameter>",
            f"              <CssParameter name=\"stroke-width\">{escape(style['stroke_width'])}</CssParameter>",
            "            </Stroke>",
            "          </LineSymbolizer>",
        ]
    )


def render_line_symbolizer_1_1(style):
    return "\n".join(
        [
            "          <se:LineSymbolizer>",
            "            <se:Stroke>",
            f"              <se:SvgParameter name=\"stroke\">{escape(style['stroke'])}</se:SvgParameter>",
            f"              <se:SvgParameter name=\"stroke-width\">{escape(style['stroke_width'])}</se:SvgParameter>",
            "            </se:Stroke>",
            "          </se:LineSymbolizer>",
        ]
    )


def render_polygon_symbolizer(style):
    return "\n".join(
        [
            "          <PolygonSymbolizer>",
            "            <Fill>",
            f"              <CssParameter name=\"fill\">{escape(style['fill'])}</CssParameter>",
            "            </Fill>",
            "            <Stroke>",
            f"              <CssParameter name=\"stroke\">{escape(style['stroke'])}</CssParameter>",
            f"              <CssParameter name=\"stroke-width\">{escape(style['stroke_width'])}</CssParameter>",
            "            </Stroke>",
            "          </PolygonSymbolizer>",
        ]
    )


def render_polygon_symbolizer_1_1(style):
    return "\n".join(
        [
            "          <se:PolygonSymbolizer>",
            "            <se:Fill>",
            f"              <se:SvgParameter name=\"fill\">{escape(style['fill'])}</se:SvgParameter>",
            "            </se:Fill>",
            "            <se:Stroke>",
            f"              <se:SvgParameter name=\"stroke\">{escape(style['stroke'])}</se:SvgParameter>",
            f"              <se:SvgParameter name=\"stroke-width\">{escape(style['stroke_width'])}</se:SvgParameter>",
            "            </se:Stroke>",
            "          </se:PolygonSymbolizer>",
        ]
    )


__all__ = [
    "build_sld_style",
    "detect_geometry_kind",
    "persist_stage_slds",
    "render_sld",
    "resolve_layer_sld_style",
    "sld_path_for_dataset",
]
