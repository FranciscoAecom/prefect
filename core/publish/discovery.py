from dataclasses import dataclass
import json
from pathlib import Path

from core.publish.metadata_xml import metadata_title
from core.publish.policy import DATA_SUFFIXES, MultiplePublishItemsError, SPATIAL_PREFIXES
from core.publish.titles import geoserver_layer_title


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

    manifest_path = find_publish_manifest(folder)
    if manifest_path:
        return discover_publish_items_from_manifest(
            manifest_path,
            store=store,
            layer=layer,
            style=style,
            layer_title=layer_title,
        )

    data_paths = sorted(
        path for path in folder.iterdir() if path.suffix.lower() in DATA_SUFFIXES
    )
    if not data_paths:
        raise FileNotFoundError(f"Nenhum arquivo de dados publicavel em: {folder}")
    if len(data_paths) > 1:
        names = ", ".join(path.name for path in data_paths)
        raise MultiplePublishItemsError(
            "Publicacao ignorada: a pasta possui mais de um conjunto de arquivos "
            f"publicavel. Mantenha exatamente um GPKG/RST/TIF, um SLD e um XML "
            f"correspondente na pasta. Dados encontrados: {names}"
        )

    return [
        build_publish_item(
            data_paths[0],
            store=store,
            layer=layer,
            style=style,
            layer_title=layer_title,
        )
    ]


def discover_publish_items_from_manifest(
    manifest_path,
    store=None,
    layer=None,
    style=None,
    layer_title=None,
):
    manifest_path = Path(manifest_path)
    manifest = load_publish_manifest(manifest_path)
    output_entries = list(iter_manifest_dataset_outputs(manifest))
    if not output_entries:
        raise FileNotFoundError(
            f"Manifest sem saidas publicaveis: {manifest_path}"
        )

    single_output = len(output_entries) == 1
    items = []
    for output_entry in output_entries:
        data_path = resolve_manifest_path(
            output_entry.get("path"),
            manifest_path.parent,
        )
        items.append(
            build_publish_item(
                data_path,
                sld_path=find_manifest_sld_path(manifest, data_path, manifest_path.parent),
                xml_path=find_manifest_xml_path(manifest, data_path, manifest_path.parent),
                store=store if single_output else None,
                layer=layer if single_output else None,
                style=style if single_output else None,
                layer_title=layer_title if single_output else None,
            )
        )
    return items


def build_publish_item(
    data_path,
    *,
    sld_path=None,
    xml_path=None,
    store=None,
    layer=None,
    style=None,
    layer_title=None,
):
    data_path = Path(data_path)
    item_layer = layer or data_path.stem
    item_store = store or item_layer
    sld_path = Path(sld_path) if sld_path else sld_path_for_data_path(data_path)
    xml_path = (
        Path(xml_path)
        if xml_path
        else data_path.parent / f"{metadata_stem_for_data_stem(data_path.stem)}.xml"
    )
    if not data_path.exists():
        raise FileNotFoundError(f"Arquivo de dados nao encontrado: {data_path}")
    if not sld_path.exists():
        raise FileNotFoundError(f"SLD nao encontrado para {data_path.name}: {sld_path}")
    if not xml_path.exists():
        raise FileNotFoundError(f"XML nao encontrado para {data_path.name}: {xml_path}")

    data_info = data_publish_info(data_path)
    item_style = style or sld_path.stem
    item_title = (
        layer_title
        or geoserver_layer_title(item_layer)
        or metadata_title(xml_path)
        or item_layer
    )
    return PublishItem(
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


def find_publish_manifest(folder):
    manifests = sorted(Path(folder).glob("*_manifest.json"))
    if not manifests:
        return None
    return manifests[0]


def load_publish_manifest(manifest_path):
    with Path(manifest_path).open("r", encoding="utf-8-sig") as file:
        manifest = json.load(file)
    if not isinstance(manifest, dict):
        raise ValueError(f"Manifest de publicacao invalido: {manifest_path}")
    return manifest


def iter_manifest_dataset_outputs(manifest):
    primary_output = manifest.get("primary_output")
    if isinstance(primary_output, dict):
        yield primary_output


def resolve_manifest_path(path_value, manifest_dir):
    if not path_value:
        raise FileNotFoundError("Manifest contem caminho de saida vazio.")
    path = Path(path_value)
    if not path.is_absolute():
        path = Path(manifest_dir) / path
    return path


def find_manifest_sld_path(manifest, data_path, manifest_dir):
    return find_manifest_companion_path(
        manifest.get("sld_files", []),
        data_path,
        manifest_dir,
        expected_names=[
            sld_path_for_data_path(data_path).name,
            data_path.with_suffix(".sld").name,
        ],
        artifact_label="SLD",
    )


def find_manifest_xml_path(manifest, data_path, manifest_dir):
    return find_manifest_companion_path(
        manifest.get("xml_files", []),
        data_path,
        manifest_dir,
        expected_name=f"{metadata_stem_for_data_stem(data_path.stem)}.xml",
        artifact_label="XML",
    )


def find_manifest_companion_path(
    artifact_paths,
    data_path,
    manifest_dir,
    *,
    expected_name=None,
    expected_names=None,
    artifact_label,
):
    names = list(expected_names or [])
    if expected_name:
        names.append(expected_name)
    resolved_paths = [
        resolve_manifest_path(path, manifest_dir)
        for path in (artifact_paths or [])
        if path
    ]
    for path in resolved_paths:
        if path.name in names:
            return path
    for name in names:
        fallback = data_path.parent / name
        if fallback.exists():
            return fallback
    raise FileNotFoundError(
        f"{artifact_label} nao encontrado para {data_path.name}: {', '.join(names)}"
    )


def metadata_stem_for_data_stem(data_stem):
    parts = data_stem.split("_", 1)
    if parts[0] in SPATIAL_PREFIXES and len(parts) == 2:
        return f"md_{parts[1]}"
    return f"md_{data_stem}"


def sld_path_for_data_path(data_path):
    data_path = Path(data_path)
    return data_path.parent / f"sld_{data_path.stem}.sld"


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


__all__ = [
    "PublishItem",
    "build_publish_item",
    "data_publish_info",
    "discover_publish_items_from_manifest",
    "discover_publish_items",
    "find_publish_manifest",
    "metadata_stem_for_data_stem",
    "sld_path_for_data_path",
]
