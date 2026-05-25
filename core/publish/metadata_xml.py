from html import escape as xml_escape
from pathlib import Path
import re
import tempfile
from xml.etree import ElementTree as ET


def metadata_title(xml_path):
    try:
        root = ET.parse(xml_path).getroot()
    except ET.ParseError:
        return ""

    namespaces = {
        "gmd": "http://www.isotc211.org/2005/gmd",
        "gco": "http://www.isotc211.org/2005/gco",
    }
    title = root.find(
        ".//gmd:identificationInfo//gmd:citation//gmd:title/gco:CharacterString",
        namespaces,
    )
    if title is not None and title.text:
        return repair_mojibake(title.text.strip())
    return ""


def metadata_uuid(xml_path):
    try:
        root = ET.parse(xml_path).getroot()
    except ET.ParseError:
        return ""
    namespaces = {
        "gmd": "http://www.isotc211.org/2005/gmd",
        "gco": "http://www.isotc211.org/2005/gco",
    }
    uuid = root.find("./gmd:fileIdentifier/gco:CharacterString", namespaces)
    if uuid is not None and uuid.text:
        return uuid.text.strip()
    return ""


def metadata_xml_with_data_dictionary_link(
    xml_path,
    data_dictionary_base_url,
    attribute_types=None,
):
    metadata_uuid_value = metadata_uuid(xml_path)
    if not metadata_uuid_value:
        return Path(xml_path), False

    dictionary_url = data_dictionary_url(data_dictionary_base_url, metadata_uuid_value)
    xml_path = Path(xml_path)
    xml_content = xml_path.read_text(encoding="utf-8")
    xml_content, updated_type_count = set_data_dictionary_field_types(
        xml_content,
        attribute_types or {},
    )
    if dictionary_url in xml_content:
        if updated_type_count == 0:
            return xml_path, False
        return write_temporary_metadata_xml(xml_content), True

    updated_content, inserted = add_data_dictionary_link(xml_content, dictionary_url)
    if not inserted:
        if updated_type_count == 0:
            return xml_path, False
        return write_temporary_metadata_xml(xml_content), True

    return write_temporary_metadata_xml(updated_content), True


def write_temporary_metadata_xml(xml_content):
    temp_file = tempfile.NamedTemporaryFile(
        delete=False,
        suffix=".xml",
        prefix="metadata_with_data_dictionary_",
    )
    temp_path = Path(temp_file.name)
    temp_file.close()
    temp_path.write_text(xml_content, encoding="utf-8")
    return temp_path


def set_data_dictionary_field_types(xml_content, attribute_types):
    if not attribute_types:
        return xml_content, 0

    dictionary_match = re.search(
        r"(?is)<data_dictionary\b[^>]*>.*?</data_dictionary>",
        xml_content,
    )
    if not dictionary_match:
        return xml_content, 0

    updated_count = 0

    def replace_field(match):
        nonlocal updated_count
        field_xml = match.group(0)
        name_match = re.search(r"(?is)<name>\s*([^<]+?)\s*</name>", field_xml)
        if not name_match:
            return field_xml

        field_name = name_match.group(1).strip()
        field_type = data_dictionary_field_type(field_name, attribute_types)
        if not field_type:
            return field_xml

        escaped_type = xml_escape(field_type, quote=True)
        if re.search(r"(?is)<type>.*?</type>", field_xml):
            updated_field = re.sub(
                r"(?is)<type>.*?</type>",
                f"<type>{escaped_type}</type>",
                field_xml,
                count=1,
            )
        else:
            updated_field = re.sub(
                r"(?is)(</field>)",
                f"  <type>{escaped_type}</type>\n\\1",
                field_xml,
                count=1,
            )

        if updated_field != field_xml:
            updated_count += 1
        return updated_field

    dictionary_xml = dictionary_match.group(0)
    updated_dictionary = re.sub(
        r"(?is)<field\b[^>]*>.*?</field>",
        replace_field,
        dictionary_xml,
    )
    updated_content = (
        xml_content[: dictionary_match.start()]
        + updated_dictionary
        + xml_content[dictionary_match.end() :]
    )
    return updated_content, updated_count


def data_dictionary_field_type(field_name, attribute_types):
    if field_name in attribute_types:
        return attribute_types[field_name]
    sdb_name = f"sdb_{field_name}"
    if sdb_name in attribute_types:
        return attribute_types[sdb_name]
    suffix_matches = [
        key for key in attribute_types if str(key).endswith(f"_{field_name}")
    ]
    if len(suffix_matches) == 1:
        return attribute_types[suffix_matches[0]]
    return ""


def data_dictionary_url(data_dictionary_base_url, metadata_uuid_value):
    return f"{str(data_dictionary_base_url).rstrip('?')}?key={metadata_uuid_value}"


def add_data_dictionary_link(xml_content, dictionary_url):
    escaped_url = xml_escape(str(dictionary_url), quote=True)
    if "Estrutura de 2 link associado" in xml_content:
        return xml_content.replace("Estrutura de 2 link associado", escaped_url), True
    updated_content, count = re.subn(
        r"<gmd:URL\s*/>",
        f"<gmd:URL>{escaped_url}</gmd:URL>",
        xml_content,
        count=1,
    )
    if count:
        return updated_content, True
    return xml_content, False


def repair_mojibake(text):
    text = str(text)
    if "\u00c3" not in text and "\u00c2" not in text:
        return text
    try:
        return text.encode("latin1").decode("utf-8")
    except UnicodeError:
        return text


__all__ = [
    "add_data_dictionary_link",
    "data_dictionary_field_type",
    "data_dictionary_url",
    "metadata_title",
    "metadata_uuid",
    "metadata_xml_with_data_dictionary_link",
    "repair_mojibake",
    "set_data_dictionary_field_types",
    "write_temporary_metadata_xml",
]
