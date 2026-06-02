import json

from core.publish.geoserver_commands import feature_type_command
from core.publish.geoserver_http import run_curl
from core.utils import log


def get_geoserver_attribute_types(item, config, auth):
    log(f"Coletando tipos dos atributos publicados no GeoServer: {item.layer}")
    response = run_curl(feature_type_command(item, config, auth), capture=True)
    try:
        payload = json.loads(response or "{}")
    except json.JSONDecodeError:
        log("Nao foi possivel interpretar os tipos retornados pelo GeoServer.")
        return {}

    attributes = payload.get("featureType", {}).get("attributes", {}).get("attribute", [])
    if isinstance(attributes, dict):
        attributes = [attributes]

    attribute_types = {}
    for attribute in attributes or []:
        name = str(attribute.get("name") or "").strip()
        if not name or name == "geom":
            continue
        mapped_type = convert_geoserver_binding(attribute.get("binding"))
        if mapped_type:
            attribute_types[name] = mapped_type

    attribute_types.setdefault("fid", "Integer64")
    log(f"Tipos coletados no GeoServer: {len(attribute_types)}")
    return attribute_types


def convert_geoserver_binding(binding):
    binding = str(binding or "")
    mappings = (
        (("String",), "String"),
        (("Long", "Integer", "Short", "BigInteger"), "Integer64"),
        (("Double", "Float", "BigDecimal"), "Real"),
        (("Boolean",), "Boolean"),
        (("Date", "Timestamp", "Time"), "Date"),
    )
    for suffixes, mapped_type in mappings:
        if binding.endswith(suffixes):
            return mapped_type
    return ""


__all__ = ["convert_geoserver_binding", "get_geoserver_attribute_types"]
