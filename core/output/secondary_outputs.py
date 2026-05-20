from core.io.dataset import write_output_gpkg
from core.output.paths import build_secondary_output_path
from core.spatial.brazil_bounds import filter_geometries_in_brazil_bounds
from core.utils import log


CORE_SECONDARY_OUTPUTS = {
    "brazil_bbox": {
        "suffix": "bbox_brasil",
        "label": "recorte bbox Brasil",
        "builder": filter_geometries_in_brazil_bounds,
    },
}


def get_registered_secondary_output_names():
    return set(CORE_SECONDARY_OUTPUTS.keys())


def persist_secondary_outputs(export_gdf, profile, theme_output_dir, base_name, persist_dataset):
    if not persist_dataset:
        return []

    output_paths = []
    for output_name in profile.get("secondary_outputs", []) or []:
        config = CORE_SECONDARY_OUTPUTS.get(output_name)
        if not config:
            log(f"Saida secundaria {output_name} nao registrada")
            continue

        output_gdf = config["builder"](export_gdf)
        output_path = build_secondary_output_path(
            theme_output_dir,
            base_name,
            config["suffix"],
        )
        log(
            f"Salvando {config['label']} em "
            f"{output_path} ({len(output_gdf)} de {len(export_gdf)} feicao(oes))"
        )
        write_output_gpkg(
            output_gdf,
            output_path,
            overwrite_existing=True,
        )
        log(f"Arquivo {config['label']} salvo com sucesso")
        output_paths.append(output_path)

    return output_paths
