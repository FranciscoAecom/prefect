from core.io.dataset import write_output_gpkg
from core.output.paths import build_secondary_output_path
from core.configured_steps import (
    get_registered_secondary_output_names,
    resolve_secondary_output_step,
)
from core.utils import log


def persist_secondary_outputs(export_gdf, profile, theme_output_dir, base_name, persist_dataset):
    if not persist_dataset:
        return []

    outputs = []
    for output_name in profile.get("secondary_outputs", []) or []:
        step = resolve_secondary_output_step(output_name)
        if not step:
            log(f"Saida secundaria {output_name} nao registrada")
            continue

        output_gdf = step.builder(export_gdf)
        output_path = build_secondary_output_path(
            theme_output_dir,
            base_name,
            step.suffix,
        )
        log(
            f"Salvando {step.label} em "
            f"{output_path} ({len(output_gdf)} de {len(export_gdf)} feicao(oes))"
        )
        write_output_gpkg(
            output_gdf,
            output_path,
            overwrite_existing=True,
        )
        log(f"Arquivo {step.label} salvo com sucesso")
        outputs.append({"path": output_path, "gdf": output_gdf})

    return outputs
