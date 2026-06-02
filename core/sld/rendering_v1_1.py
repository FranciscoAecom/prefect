from xml.sax.saxutils import escape

from core.sld.rendering import style_value


def render_sld(layer_name, geometry_kind, style):
    rules = render_rules(geometry_kind, style)
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
            rules,
            "      </se:FeatureTypeStyle>",
            "    </UserStyle>",
            "  </NamedLayer>",
            "</StyledLayerDescriptor>",
            "",
        ]
    )


def render_rules(geometry_kind, style):
    if not style.get("rules"):
        return "\n".join(
            [
                "        <se:Rule>",
                f"          <se:Name>{escape(style['rule_name'])}</se:Name>",
                render_symbolizer(geometry_kind, style),
                "        </se:Rule>",
            ]
        )
    return "\n".join(render_rule(geometry_kind, rule) for rule in style["rules"])


def render_rule(geometry_kind, rule):
    rule_name = rule.get("name", "Rule")
    title = rule.get("title", rule_name)
    return "\n".join(
        [
            "        <se:Rule>",
            f"          <se:Name>{escape(rule_name)}</se:Name>",
            "          <se:Description>",
            f"            <se:Title>{escape(title)}</se:Title>",
            "          </se:Description>",
            render_filter(rule.get("filter", {})),
            render_symbolizer(geometry_kind, rule),
            "        </se:Rule>",
        ]
    )


def render_filter(rule_filter):
    property_name = rule_filter.get("property")
    literal = rule_filter.get("literal")
    if not property_name or literal is None:
        return ""
    return "\n".join(
        [
            '          <ogc:Filter xmlns:ogc="http://www.opengis.net/ogc">',
            "            <ogc:PropertyIsEqualTo>",
            f"              <ogc:PropertyName>{escape(property_name)}</ogc:PropertyName>",
            f"              <ogc:Literal>{escape(literal)}</ogc:Literal>",
            "            </ogc:PropertyIsEqualTo>",
            "          </ogc:Filter>",
        ]
    )


def render_symbolizer(geometry_kind, style):
    if geometry_kind == "polygon":
        return render_polygon_symbolizer(style.get("polygon", {}))
    if geometry_kind == "line":
        return render_line_symbolizer(style.get("line", {}))
    return render_point_symbolizer(style.get("point", {}))


def render_point_symbolizer(style):
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
            "          <se:LineSymbolizer>",
            "            <se:Stroke>",
            f"              <se:SvgParameter name=\"stroke\">{escape(style['stroke'])}</se:SvgParameter>",
            f"              <se:SvgParameter name=\"stroke-width\">{escape(style['stroke_width'])}</se:SvgParameter>",
            "            </se:Stroke>",
            "          </se:LineSymbolizer>",
        ]
    )


def render_polygon_symbolizer(style):
    lines = ["          <se:PolygonSymbolizer>"]
    if "fill" in style:
        lines.extend(
            [
                "            <se:Fill>",
                f"              <se:SvgParameter name=\"fill\">{escape(style['fill'])}</se:SvgParameter>",
                "            </se:Fill>",
            ]
        )
    if "stroke" in style:
        stroke_linejoin = style_value(style, "stroke_linejoin", "stroke-linejoin")
        lines.extend(
            [
                "            <se:Stroke>",
                f"              <se:SvgParameter name=\"stroke\">{escape(style['stroke'])}</se:SvgParameter>",
                f"              <se:SvgParameter name=\"stroke-width\">{escape(style.get('stroke_width', '0.5'))}</se:SvgParameter>",
            ]
        )
        if stroke_linejoin:
            lines.append(
                f"              <se:SvgParameter name=\"stroke-linejoin\">{escape(stroke_linejoin)}</se:SvgParameter>"
            )
        lines.append("            </se:Stroke>")
    lines.append("          </se:PolygonSymbolizer>")
    return "\n".join(lines)
