from prefect import flow

from core.prefect_support.run_names import flow_run_name
from core.treatment.service import run_data_treatment


@flow(name="Data Treatment", flow_run_name=flow_run_name, log_prints=True)
def data_treatment_flow(output_base=None, theme_folders=None, source_path_overrides=None, force=False):
    return run_data_treatment(
        output_base=output_base,
        theme_folders=theme_folders,
        source_path_overrides=source_path_overrides,
        force=force,
    )


__all__ = ["data_treatment_flow"]
