from pathlib import Path
from xml.etree import ElementTree as ET


SLD_NS = "http://www.opengis.net/sld"
SE_NS = "http://www.opengis.net/se"


def prepare_sld_for_upload(sld_path, style_name, layer_name):
    sld_path = Path(sld_path)
    tree = ET.parse(sld_path)
    root = tree.getroot()
    namespaces = {"sld": SLD_NS, "se": SE_NS}

    for path in (
        "./sld:NamedLayer/sld:Name",
        "./sld:NamedLayer/se:Name",
        "./sld:NamedLayer/sld:UserStyle/sld:Name",
        "./sld:NamedLayer/sld:UserStyle/se:Name",
        "./sld:UserLayer/sld:UserStyle/sld:Name",
        "./sld:UserLayer/sld:UserStyle/se:Name",
    ):
        node = root.find(path, namespaces)
        if node is None:
            continue
        if path.endswith("UserStyle/sld:Name") or path.endswith("UserStyle/se:Name"):
            node.text = style_name
        else:
            node.text = layer_name

    upload_path = sld_path.parent / f".{sld_path.stem}.upload.sld"
    tree.write(upload_path, encoding="UTF-8", xml_declaration=True)
    return upload_path
