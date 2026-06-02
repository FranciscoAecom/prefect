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
                'xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" '
                'xsi:schemaLocation="http://www.opengis.net/sld '
                f'http://schemas.opengis.net/sld/{escape(style["version"])}/StyledLayerDescriptor.xsd">'
            ),
            "  <NamedLayer>",
            f"    <Name>{escape(layer_name)}</Name>",
            "    <UserStyle>",
            f"      <Name>{escape(layer_name)}</Name>",
            "      <FeatureTypeStyle>",
            rules,
            "      </FeatureTypeStyle>",
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
                "        <Rule>",
                f"          <Name>{escape(style['rule_name'])}</Name>",
                render_symbolizer(geometry_kind, style),
                "        </Rule>",
            ]
        )
    return "\n".join(render_rule(geometry_kind, rule) for rule in style["rules"])


def render_rule(geometry_kind, rule):
    rule_name = rule.get("name", "Rule")
    title = rule.get("title", rule_name)
    return "\n".join(
        [
            "        <Rule>",
            f"          <Name>{escape(rule_name)}</Name>",
            f"          <Title>{escape(title)}</Title>",
            render_filter(rule.get("filter", {})),
            render_symbolizer(geometry_kind, rule),
            "        </Rule>",
        ]
    )


def render_filter(rule_filter):
    property_name = rule_filter.get("property")
    literal = rule_filter.get("literal")
    if not property_name or literal is None:
        return ""
    return "\n".join(
        [
            "          <ogc:Filter>",
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


def render_polygon_symbolizer(style):
    lines = ["          <PolygonSymbolizer>"]
    if "fill" in style:
        lines.extend(
            [
                "            <Fill>",
                f"              <CssParameter name=\"fill\">{escape(style['fill'])}</CssParameter>",
                "            </Fill>",
            ]
        )
    if "stroke" in style:
        stroke_linejoin = style_value(style, "stroke_linejoin", "stroke-linejoin")
        lines.extend(
            [
                "            <Stroke>",
                f"              <CssParameter name=\"stroke\">{escape(style['stroke'])}</CssParameter>",
                f"              <CssParameter name=\"stroke-width\">{escape(style.get('stroke_width', '0.5'))}</CssParameter>",
            ]
        )
        if stroke_linejoin:
            lines.append(
                f"              <CssParameter name=\"stroke-linejoin\">{escape(stroke_linejoin)}</CssParameter>"
            )
        lines.append("            </Stroke>")
    lines.append("          </PolygonSymbolizer>")
    return "\n".join(lines)
