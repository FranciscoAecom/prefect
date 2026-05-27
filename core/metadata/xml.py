from __future__ import annotations

import re
from datetime import datetime
from pathlib import Path
from xml.sax.saxutils import escape

import pandas as pd

from core.ingest.normalization import normalize_attribute_name, normalize_lookup_value, stringify
from core.io.dataset import inspect_input_attributes
from core.utils import log
from settings import DICTIONARIES_SHEET_NAME, INGEST_WORKBOOK_PATH


TEMPLATE_DIR = Path(__file__).resolve().parent / "templates"
BRONZE_TEMPLATE_PATH = TEMPLATE_DIR / "template_xml_bronze.xml"
SILVER_TEMPLATE_PATH = TEMPLATE_DIR / "template_xml_silver.xml"
PLACEHOLDER_PATTERN = re.compile(r"%([A-Za-z0-9_]+)%")
DATA_DICTIONARY_PATTERN = re.compile(
    r"(?P<open>\s*<data_dictionary>)\s*</data_dictionary>",
    flags=re.DOTALL,
)
GEOMETRY_FILE_PREFIX_PATTERN = re.compile(r"^(pnt|pol|lin)(?=_)")


def persist_stage_metadata_xmls(
    record,
    silver_gdf,
    silver_output_paths,
    base_name,
    persist_dataset=True,
):
    if not persist_dataset:
        return []

    outputs = []
    descriptions = load_dictionary_descriptions()

    for output_path in silver_output_paths:
        xml_path = persist_silver_metadata_xml(
            record,
            silver_gdf,
            Path(output_path),
            descriptions,
        )
        if xml_path:
            outputs.append(xml_path)

    if outputs:
        log(
            "Metadados XML gerados: "
            + ", ".join(str(path) for path in outputs)
        )
    return outputs


def persist_bronze_metadata_xml(
    record,
    bronze_dataset_path,
    descriptions,
    base_name,
    fallback_gdf=None,
):
    bronze_dir_value = stringify(getattr(record, "bronze_dir", ""))
    if not bronze_dir_value:
        return None
    bronze_dir = Path(bronze_dir_value)
    if not bronze_dataset_path:
        return None
    bronze_dataset_path = Path(bronze_dataset_path)

    fields = [
        bronze_field_name(field)
        for field in inspect_dataset_fields(
            bronze_dataset_path,
            fallback_gdf=fallback_gdf,
        )
        if should_include_dictionary_field(field, stage="bronze")
    ]
    xml_path = bronze_dir / metadata_xml_name_for_base(base_name)
    render_and_write_metadata_xml(
        template_path=BRONZE_TEMPLATE_PATH,
        output_path=xml_path,
        record=record,
        stage="bronze",
        fields=fields,
        descriptions=descriptions,
    )
    return xml_path


def persist_silver_metadata_xml(record, silver_gdf, output_path, descriptions):
    fields = [
        str(field)
        for field in inspect_dataset_fields(output_path, fallback_gdf=silver_gdf)
        if should_include_dictionary_field(field, stage="silver")
    ]
    xml_path = metadata_xml_path_for_dataset(output_path)
    render_and_write_metadata_xml(
        template_path=SILVER_TEMPLATE_PATH,
        output_path=xml_path,
        record=record,
        stage="silver",
        fields=fields,
        descriptions=descriptions,
    )
    return xml_path


def find_first_geographic_dataset(directory):
    directory = Path(directory)
    if not directory.exists():
        return None
    for suffix in (".gpkg", ".shp"):
        matches = sorted(
            candidate
            for candidate in directory.rglob(f"*{suffix}")
            if candidate.is_file()
        )
        if matches:
            return matches[0]
    return None


def inspect_dataset_fields(path, fallback_gdf=None):
    path = Path(path)
    if fallback_gdf is not None:
        return list(fallback_gdf.columns)
    if path.exists() and path.suffix.lower() in {".gpkg", ".shp"}:
        return inspect_input_attributes(path)
    return []


def metadata_xml_path_for_dataset(dataset_path):
    dataset_path = Path(dataset_path)
    return dataset_path.with_name(metadata_xml_name_for_base(dataset_path.stem))


def metadata_xml_name_for_base(base_name):
    base_name = stringify(base_name) or "metadata"
    metadata_stem = GEOMETRY_FILE_PREFIX_PATTERN.sub("md", base_name, count=1)
    if metadata_stem == base_name and not metadata_stem.startswith("md_"):
        metadata_stem = f"md_{metadata_stem}"
    return f"{metadata_stem}.xml"


def render_and_write_metadata_xml(
    template_path,
    output_path,
    record,
    stage,
    fields,
    descriptions,
):
    template = Path(template_path).read_text(encoding="utf-8")
    replacements = build_template_replacements(record)
    rendered = replace_placeholders(template, replacements)
    dictionary_xml = build_data_dictionary_xml(
        fields,
        record=record,
        stage=stage,
        descriptions=descriptions,
    )
    rendered = replace_data_dictionary_block(rendered, dictionary_xml)

    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(rendered, encoding="utf-8")


def build_template_replacements(record):
    date_stamp = format_xml_date(getattr(record, "date_stamp", "")) or datetime.now().strftime(
        "%Y-%m-%d"
    )
    date_value = format_xml_date(getattr(record, "date", ""))
    return {
        "id_geonetwork": stringify(getattr(record, "id_geonetwork", "")),
        "responsible_party": stringify(getattr(record, "responsible_party", "")),
        "date_stamp": date_stamp,
        "reference_system": stringify(getattr(record, "reference_system", "")),
        "theme": stringify(getattr(record, "theme", "")),
        "date": date_value,
        "abstract": stringify(getattr(record, "abstract", "")),
        "topic_category_code": stringify(getattr(record, "topic_category_code", "")),
        "beginposition": format_xml_date(getattr(record, "beginposition", "")),
        "endposition": format_xml_date(getattr(record, "endposition", "")),
        "source": stringify(getattr(record, "source", "")),
        "citation": stringify(getattr(record, "citation", "")),
        "data_dictionary": stringify(getattr(record, "data_dictionary", "")),
        "metadata": stringify(getattr(record, "metadata", "")),
        "methodologie": stringify(getattr(record, "methodologie", "")),
        "others": stringify(getattr(record, "others", "")),
        "category_acronym": stringify(getattr(record, "category_acronym", "")),
        "project": stringify(getattr(record, "project", "")),
        "data_classification": stringify(getattr(record, "data_classification", "")),
        "data_activity_classification": stringify(
            getattr(record, "data_activity_classification", "")
        ),
        "maintenance_frequency_aecom": stringify(
            getattr(record, "maintenance_frequency_aecom", "")
        ),
        "characterstring": stringify(getattr(record, "characterstring", "")),
    }


def format_xml_date(value):
    text = stringify(value)
    if not text:
        return ""
    parsed = pd.to_datetime(value, errors="coerce")
    if pd.isna(parsed):
        if " 00:00:00" in text:
            return text.split(" ")[0]
        return text
    return parsed.strftime("%Y-%m-%d")


def replace_placeholders(template, replacements):
    def substitute(match):
        return escape(replacements.get(match.group(1), ""))

    return PLACEHOLDER_PATTERN.sub(substitute, template)


def replace_data_dictionary_block(template, dictionary_xml):
    match = DATA_DICTIONARY_PATTERN.search(template)
    if not match:
        return template
    return (
        template[: match.start()]
        + f"{match.group('open')}\n{dictionary_xml}\n  </data_dictionary>"
        + template[match.end() :]
    )


def build_data_dictionary_xml(fields, record, stage, descriptions):
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
            log(
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
            lookup_description(
                descriptions,
                theme,
                normalized_field,
                preferred="aecom",
            )
            or lookup_description(
                descriptions,
                "AECOM",
                normalized_field,
                preferred="aecom",
            )
        )

    if stage == "bronze":
        return lookup_description(
            descriptions,
            theme,
            normalized_field,
            preferred="original",
        )

    return lookup_description(
        descriptions,
        theme,
        normalized_field,
        preferred="aecom",
    )


def lookup_description(descriptions, theme, field, preferred):
    theme_key = normalize_lookup_value(theme)
    field_key = normalize_attribute_name(field)
    theme_entry = descriptions.get(theme_key, {})

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
    workbook_path = workbook_path or INGEST_WORKBOOK_PATH
    sheet_name = sheet_name or DICTIONARIES_SHEET_NAME
    dataframe = pd.read_excel(workbook_path, sheet_name=sheet_name)
    descriptions = {}

    for _, row in dataframe.iterrows():
        theme = stringify(row.get("theme"))
        theme_key = normalize_lookup_value(theme)
        if not theme_key:
            continue

        entry = descriptions.setdefault(
            theme_key,
            {"original": {}, "aecom": {}},
        )
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
    if not field or field == "geometry":
        return False
    return True


__all__ = [
    "build_data_dictionary_xml",
    "format_xml_date",
    "load_dictionary_descriptions",
    "metadata_xml_name_for_base",
    "metadata_xml_path_for_dataset",
    "persist_bronze_metadata_xml",
    "persist_stage_metadata_xmls",
    "render_and_write_metadata_xml",
]
