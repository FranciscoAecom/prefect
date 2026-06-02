from pathlib import Path

from core.sld.rendering_v1_0 import render_sld as render_sld_1_0
from core.sld.rendering_v1_1 import render_sld as render_sld_1_1
from core.utils import log


SLD_OMITTED_DATASET_PREFIXES = {"pnt", "pol", "lin", "rst"}


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
        sld_path, sld_text = build_output_sld(output, base_style)
        write_sld_file(sld_path, sld_text)
        sld_paths.append(sld_path)

    if sld_paths:
        log("Arquivos SLD gerados: " + ", ".join(str(path) for path in sld_paths))
    return sld_paths


def build_output_sld(output, base_style):
    output_path = Path(output["path"])
    style = resolve_layer_sld_style(base_style, output_path.stem)
    sld_path = sld_path_for_dataset(output_path)
    sld_text = render_sld(
        layer_name=output_path.stem,
        geometry_kind=detect_geometry_kind(output.get("gdf")),
        style=style,
    )
    return sld_path, sld_text


def write_sld_file(sld_path, sld_text):
    Path(sld_path).write_text(sld_text, encoding="utf-8")


def build_sld_style(rule_profile):
    configured = rule_profile.get("sld", {}) if isinstance(rule_profile, dict) else {}
    style = {
        "version": DEFAULT_SLD_STYLE["version"],
        "rule_name": DEFAULT_SLD_STYLE["rule_name"],
        "point": dict(DEFAULT_SLD_STYLE["point"]),
        "line": dict(DEFAULT_SLD_STYLE["line"]),
        "polygon": dict(DEFAULT_SLD_STYLE["polygon"]),
        "rules": [],
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
            apply_style_mapping(style[section], configured[section])

    if isinstance(configured.get("rules"), list):
        style["rules"] = normalize_sld_rules(configured["rules"])

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
    if isinstance(layer_style.get("rules"), list):
        normalized["rules"] = normalize_sld_rules(layer_style["rules"])
    return normalized


def normalize_sld_rules(rules):
    normalized = []
    for rule in rules:
        if not isinstance(rule, dict):
            continue
        normalized_rule = {}
        for key in ("name", "title"):
            if isinstance(rule.get(key), str) and rule[key].strip():
                normalized_rule[key] = rule[key].strip()
        if isinstance(rule.get("filter"), dict):
            normalized_rule["filter"] = normalize_style_mapping(rule["filter"])
        for section in ("point", "line", "polygon"):
            if isinstance(rule.get(section), dict):
                normalized_rule[section] = normalize_style_mapping(rule[section])
        if normalized_rule:
            normalized.append(normalized_rule)
    return normalized


def normalize_style_mapping(style_mapping):
    return {
        str(key): str(value)
        for key, value in style_mapping.items()
        if value is not None
    }


def apply_style_mapping(target, configured):
    for key, value in configured.items():
        key = str(key)
        if value is None:
            target.pop(key, None)
            continue
        target[key] = str(value)


def resolve_layer_sld_style(base_style, layer_name):
    style = {
        "version": base_style["version"],
        "rule_name": base_style["rule_name"],
        "point": dict(base_style["point"]),
        "line": dict(base_style["line"]),
        "polygon": dict(base_style["polygon"]),
        "rules": list(base_style.get("rules", [])),
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
    if isinstance(layer_style.get("rules"), list):
        style["rules"] = list(layer_style["rules"])
    return style


def sld_path_for_dataset(dataset_path):
    dataset_path = Path(dataset_path)
    return dataset_path.parent / f"sld_{sld_stem_for_dataset_stem(dataset_path.stem)}.sld"


def sld_stem_for_dataset_stem(dataset_stem):
    parts = str(dataset_stem).split("_", 1)
    if parts[0] in SLD_OMITTED_DATASET_PREFIXES and len(parts) == 2:
        return parts[1]
    return str(dataset_stem)


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


__all__ = [
    "build_output_sld",
    "build_sld_style",
    "detect_geometry_kind",
    "persist_stage_slds",
    "render_sld",
    "resolve_layer_sld_style",
    "SLD_OMITTED_DATASET_PREFIXES",
    "sld_path_for_dataset",
    "sld_stem_for_dataset_stem",
    "write_sld_file",
]
