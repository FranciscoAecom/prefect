from dataclasses import dataclass
from pathlib import Path
from xml.etree import ElementTree as ET


DATA_SUFFIXES = {".gpkg", ".rst", ".tif"}
SPATIAL_PREFIXES = {"pnt", "pol", "lin", "rst"}


@dataclass(frozen=True)
class PublishItem:
    data_path: Path
    sld_path: Path
    xml_path: Path
    store: str
    layer: str
    style: str
    layer_title: str
    data_type: str
    data_content_type: str
    data_endpoint: str
    layer_resource: str
    data_label: str


def discover_publish_items(folder, store=None, layer=None, style=None, layer_title=None):
    folder = Path(folder)
    if not folder.exists():
        raise FileNotFoundError(f"Pasta de publicacao nao encontrada: {folder}")

    items = []
    for data_path in sorted(
        path for path in folder.iterdir() if path.suffix.lower() in DATA_SUFFIXES
    ):
        item_layer = layer or data_path.stem
        item_store = store or item_layer
        sld_path = data_path.with_suffix(".sld")
        xml_path = folder / f"{metadata_stem_for_data_stem(data_path.stem)}.xml"
        if not sld_path.exists():
            raise FileNotFoundError(f"SLD nao encontrado para {data_path.name}: {sld_path}")
        if not xml_path.exists():
            raise FileNotFoundError(f"XML nao encontrado para {data_path.name}: {xml_path}")

        data_info = data_publish_info(data_path)
        item_style = style or sld_path.stem
        item_title = layer_title or metadata_title(xml_path) or item_layer
        items.append(
            PublishItem(
                data_path=data_path,
                sld_path=sld_path,
                xml_path=xml_path,
                store=item_store,
                layer=item_layer,
                style=item_style,
                layer_title=item_title,
                data_type=data_info["type"],
                data_content_type=data_info["content_type"],
                data_endpoint=data_info["endpoint"],
                layer_resource=data_info["layer_resource"],
                data_label=data_info["label"],
            )
        )

    if not items:
        raise FileNotFoundError(f"Nenhum arquivo de dados publicavel em: {folder}")
    return items


def metadata_stem_for_data_stem(data_stem):
    parts = data_stem.split("_", 1)
    if parts[0] in SPATIAL_PREFIXES and len(parts) == 2:
        return f"md_{parts[1]}"
    return f"md_{data_stem}"


def data_publish_info(data_path):
    suffix = Path(data_path).suffix.lower()
    if suffix == ".gpkg":
        return {
            "type": "gpkg",
            "content_type": "application/geopackage+vnd.sqlite3",
            "endpoint": "datastores",
            "layer_resource": "featuretypes",
            "label": "GPKG",
        }
    if suffix == ".rst":
        return {
            "type": "rst",
            "content_type": "application/octet-stream",
            "endpoint": "coveragestores",
            "layer_resource": "coverages",
            "label": "RST",
        }
    if suffix == ".tif":
        return {
            "type": "geotiff",
            "content_type": "image/tiff",
            "endpoint": "coveragestores",
            "layer_resource": "coverages",
            "label": "TIFF",
        }
    raise ValueError(f"Tipo de arquivo nao suportado: {suffix}")


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
        return title.text.strip()
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
