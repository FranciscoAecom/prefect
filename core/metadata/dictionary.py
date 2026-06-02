import pandas as pd
from xml.sax.saxutils import escape

from core.ingest.normalization import normalize_attribute_name, normalize_lookup_value, stringify
from core.utils import log
from settings import DICTIONARIES_SHEET_NAME, INGEST_WORKBOOK_PATH


def build_data_dictionary_xml(fields, record, stage, descriptions, log_fn=log):
    theme = stringify(getattr(record, "theme", ""))
    lines = []
    for field in fields:
        if not should_include_dictionary_field(field, stage=stage):
            continue
        description = resolve_field_description(
            field,
            theme=theme,
            stage=stage,
            descriptions=descriptions,
        )
        if not description:
            log_fn(
                "Descricao de atributo nao encontrada na aba dictionaries; "
                f"campo sera mantido no XML com descricao vazia: {field}"
            )
        lines.extend(
            [
                "    <field>",
                f"      <name>{escape(field)}</name>",
                f"      <description>{escape(description)}</description>",
                "    </field>",
            ]
        )
    return "\n".join(lines)


def resolve_field_description(field, theme, stage, descriptions):
    normalized_field = normalize_attribute_name(field)
    if not normalized_field:
        return ""

    if normalized_field.startswith("acm_"):
        return (
            lookup_description(descriptions, theme, normalized_field, preferred="aecom")
            or lookup_description(descriptions, "AECOM", normalized_field, preferred="aecom")
        )
    if stage == "bronze":
        return lookup_description(descriptions, theme, normalized_field, preferred="original")
    return lookup_description(descriptions, theme, normalized_field, preferred="aecom")


def lookup_description(descriptions, theme, field, preferred):
    theme_entry = descriptions.get(normalize_lookup_value(theme), {})
    field_key = normalize_attribute_name(field)
    if preferred == "original":
        candidates = (
            ("original", field_key),
            ("aecom", ensure_sdb_field_name(field_key)),
            ("aecom", field_key),
        )
    else:
        candidates = (
            ("aecom", field_key),
            ("aecom", ensure_sdb_field_name(field_key)),
            ("original", strip_sdb_prefix(field_key)),
            ("original", field_key),
        )
    for namespace, candidate in candidates:
        description = theme_entry.get(namespace, {}).get(candidate)
        if description:
            return description
    return ""


def load_dictionary_descriptions(workbook_path=None, sheet_name=None):
    dataframe = pd.read_excel(
        workbook_path or INGEST_WORKBOOK_PATH,
        sheet_name=sheet_name or DICTIONARIES_SHEET_NAME,
    )
    descriptions = {}
    for _, row in dataframe.iterrows():
        theme_key = normalize_lookup_value(stringify(row.get("theme")))
        if not theme_key:
            continue
        entry = descriptions.setdefault(theme_key, {"original": {}, "aecom": {}})
        original_name = normalize_attribute_name(row.get("original_attribute_name"))
        aecom_name = normalize_attribute_name(row.get("aecom_attribute_name"))
        original_description = stringify(row.get("original_description"))
        aecom_description = stringify(row.get("aecom_description"))
        if original_name:
            set_description_if_present(
                entry["original"],
                original_name,
                original_description or aecom_description,
            )
        if aecom_name:
            set_description_if_present(
                entry["aecom"],
                aecom_name,
                aecom_description or original_description,
            )
    return descriptions


def set_description_if_present(target, field_name, description):
    if field_name not in target or (description and not target[field_name]):
        target[field_name] = description


def bronze_field_name(field):
    return strip_sdb_prefix(normalize_attribute_name(field))


def strip_sdb_prefix(field):
    field = normalize_attribute_name(field)
    if field.startswith("sdb_"):
        return field.removeprefix("sdb_")
    return field


def ensure_sdb_field_name(field):
    field = normalize_attribute_name(field)
    if not field or field.startswith(("sdb_", "acm_")):
        return field
    return f"sdb_{field}"


def should_include_dictionary_field(field, stage=None):
    field = normalize_attribute_name(field)
    return bool(field and field != "geometry")


__all__ = [
    "bronze_field_name",
    "build_data_dictionary_xml",
    "ensure_sdb_field_name",
    "load_dictionary_descriptions",
    "lookup_description",
    "resolve_field_description",
    "set_description_if_present",
    "should_include_dictionary_field",
    "strip_sdb_prefix",
]
