import json
import re
from pathlib import Path


HEX_COLOR_PATTERN = re.compile(r"^#?[0-9A-Fa-f]{6}$")


def generate_categorized_style_from_domain(
    rules_dir,
    field_name,
    palette_path,
    output_path=None,
    geometry_kind="point",
    usage_column="uso_localidades",
    default_color_value=None,
    rule_name=None,
):
    rules_dir = Path(rules_dir)
    values = load_domain_accepted_values(rules_dir / "domains.json", field_name)
    palette_colors = load_palette_colors(palette_path)
    color_assignments = load_palette_assignments(palette_path, usage_column=usage_column)
    style = build_categorized_sld_style(
        field_name=field_name,
        values=values,
        palette_colors=palette_colors,
        colors_by_value=color_assignments,
        geometry_kind=geometry_kind,
        default_color_value=default_color_value,
        rule_name=rule_name,
    )

    output_path = Path(output_path) if output_path else rules_dir / "style.json"
    write_style_json(output_path, style)
    return style


def build_categorized_sld_style(
    *,
    field_name,
    values,
    palette_colors,
    colors_by_value=None,
    geometry_kind="point",
    version="1.1.0",
    rule_name=None,
    default_color_value=None,
):
    values = [str(value) for value in values if str(value).strip()]
    if not values:
        raise ValueError("Nenhum valor de dominio informado para gerar o style.json.")

    colors_by_value = {
        str(value): normalize_hex_color(color)
        for value, color in (colors_by_value or {}).items()
        if str(value).strip() and str(color).strip()
    }
    palette_colors = [normalize_hex_color(color) for color in palette_colors]
    assigned_colors = assign_colors_to_values(values, palette_colors, colors_by_value)
    default_color = assigned_colors.get(default_color_value) if default_color_value else None
    default_color = default_color or assigned_colors[values[0]]

    geometry_kind = normalize_geometry_kind(geometry_kind)
    sld = {
        "version": version,
        "rule_name": rule_name or f"Categorias de {field_name}",
        geometry_kind: default_symbolizer(geometry_kind, default_color),
        "rules": [
            {
                "name": value,
                "title": value,
                "filter": {
                    "property": field_name,
                    "literal": value,
                },
                geometry_kind: default_symbolizer(geometry_kind, assigned_colors[value]),
            }
            for value in values
        ],
    }
    return {"sld": sld}


def assign_colors_to_values(values, palette_colors, colors_by_value):
    assigned = {}
    fallback_colors = [color for color in palette_colors if color not in colors_by_value.values()]
    fallback_index = 0

    for value in values:
        if value in colors_by_value:
            assigned[value] = colors_by_value[value]
            continue
        if fallback_index >= len(fallback_colors):
            raise ValueError(
                "Paleta sem cores suficientes para os valores sem atribuicao explicita."
            )
        assigned[value] = fallback_colors[fallback_index]
        fallback_index += 1
    return assigned


def load_domain_accepted_values(domains_path, field_name):
    domains = json.loads(Path(domains_path).read_text(encoding="utf-8-sig"))
    fields = domains.get("fields", domains)
    field = fields.get(field_name)
    if not isinstance(field, dict):
        raise KeyError(f"Campo nao encontrado em domains.json: {field_name}")
    values = field.get("accepted_values", [])
    if not isinstance(values, list):
        raise ValueError(f"Campo {field_name}.accepted_values deve ser uma lista.")
    return values


def load_palette_colors(palette_path):
    rows = load_palette_rows(palette_path)
    colors = []
    for row in rows:
        color = row.get("hex", "")
        if color:
            normalized = normalize_hex_color(color)
            if normalized not in colors:
                colors.append(normalized)
    return colors


def load_palette_assignments(palette_path, usage_column="uso_localidades"):
    assignments = {}
    for row in load_palette_rows(palette_path):
        usage = row.get(usage_column, "").strip()
        color = row.get("hex", "").strip()
        if usage and color:
            assignments[usage] = normalize_hex_color(color)
    return assignments


def load_palette_rows(palette_path):
    rows = []
    table_headers = None
    for line in Path(palette_path).read_text(encoding="utf-8").splitlines():
        if not line.strip().startswith("|"):
            continue
        cells = split_markdown_table_row(line)
        if not cells:
            continue
        if table_headers is None:
            table_headers = [normalize_header(cell) for cell in cells]
            continue
        if is_markdown_separator(cells):
            continue
        if len(cells) != len(table_headers):
            continue
        rows.append(dict(zip(table_headers, cells)))
    return rows


def split_markdown_table_row(line):
    return [cell.strip().strip("`") for cell in line.strip().strip("|").split("|")]


def normalize_header(value):
    return value.strip().lower()


def is_markdown_separator(cells):
    return all(set(cell.replace(":", "").strip()) <= {"-"} for cell in cells)


def normalize_hex_color(value):
    text = str(value).strip()
    if not HEX_COLOR_PATTERN.match(text):
        raise ValueError(f"Cor hexadecimal invalida: {value}")
    if not text.startswith("#"):
        text = f"#{text}"
    return text.upper()


def normalize_geometry_kind(value):
    geometry_kind = str(value or "").strip().lower()
    if geometry_kind not in {"point", "line", "polygon"}:
        raise ValueError("geometry_kind deve ser point, line ou polygon.")
    return geometry_kind


def default_symbolizer(geometry_kind, color):
    if geometry_kind == "line":
        return {
            "stroke": color,
            "stroke_width": "1.2",
        }
    if geometry_kind == "polygon":
        return {
            "fill": color,
            "stroke": "#232323",
            "stroke_width": "0.5",
        }
    return {
        "well_known_name": "circle",
        "fill": color,
        "stroke": "#232323",
        "stroke_width": "0.5",
        "size": "7",
    }


def write_style_json(path, style):
    Path(path).write_text(
        json.dumps(style, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )


__all__ = [
    "assign_colors_to_values",
    "build_categorized_sld_style",
    "generate_categorized_style_from_domain",
    "load_domain_accepted_values",
    "load_palette_assignments",
    "load_palette_colors",
    "load_palette_rows",
    "normalize_hex_color",
    "write_style_json",
]
