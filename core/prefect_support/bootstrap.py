import os
import subprocess
import sys

from core.config.defaults import (
    DEFAULT_CAR_PUBLIC_API_BASE,
    DEFAULT_DOWNLOAD_ARCHIVE_BASE,
    DEFAULT_DOWNLOAD_EXTRACT_BASE,
    DEFAULT_MUNICIPALITIES_BASE_PATH,
)
from core.prefect_support.blocks import save_default_blocks
from core.prefect_support.variables import set_prefect_variable


DEFAULT_WORK_POOLS = ("local-treatment", "local-publish")


def set_default_variables(print_fn=print):
    variables = {
        "car_public_api_base": DEFAULT_CAR_PUBLIC_API_BASE,
        "download_archive_base": str(DEFAULT_DOWNLOAD_ARCHIVE_BASE),
        "download_extract_base": str(DEFAULT_DOWNLOAD_EXTRACT_BASE),
    }
    if DEFAULT_MUNICIPALITIES_BASE_PATH:
        variables["municipios_base_path"] = str(DEFAULT_MUNICIPALITIES_BASE_PATH)
    for name, value in variables.items():
        set_prefect_variable(name, value, tags=["data-pipeline", "config"])
        print_fn(f"Variable definida: {name}={value}")


def set_default_blocks(print_fn=print):
    summary = save_default_blocks(overwrite=True)
    for name in summary["saved"]:
        print_fn(f"Block definido: {name}")
    for name in summary["skipped"]:
        print_fn(f"Block ignorado sem credenciais no ambiente: {name}")


def set_default_work_pools(print_fn=print):
    env = dict(os.environ)
    env.setdefault("PYTHONIOENCODING", "utf-8")
    for work_pool in DEFAULT_WORK_POOLS:
        subprocess.run(
            [
                sys.executable,
                "-m",
                "prefect",
                "work-pool",
                "create",
                work_pool,
                "--type",
                "process",
                "--overwrite",
            ],
            check=True,
            env=env,
        )
        print_fn(f"Work Pool definido: {work_pool}")


def bootstrap_prefect(create_automation, print_fn=print):
    set_default_variables(print_fn=print_fn)
    set_default_blocks(print_fn=print_fn)
    set_default_work_pools(print_fn=print_fn)
    create_automation()


__all__ = [
    "DEFAULT_WORK_POOLS",
    "bootstrap_prefect",
    "set_default_blocks",
    "set_default_variables",
    "set_default_work_pools",
]
