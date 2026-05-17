import asyncio
import logging
from time import sleep

from prefect.client.orchestration import get_client

from core.prefect_support.run_names import scheduled_flow_run_name


DEPLOYMENT_NAME = "Data Pipeline/UR CAR - 27 bases"
LOGGER = logging.getLogger(__name__)


async def rename_scheduled_runs(deployment_name=DEPLOYMENT_NAME, print_summary=True):
    async with get_client() as client:
        deployment = await client.read_deployment_by_name(deployment_name)
        renamed_count = 0
        offset = 0

        while True:
            flow_runs = await client.read_flow_runs(limit=200, offset=offset)
            if not flow_runs:
                break

            for flow_run in flow_runs:
                if flow_run.deployment_id != deployment.id:
                    continue
                if getattr(flow_run.state_type, "value", flow_run.state_type) != "SCHEDULED":
                    continue

                new_name = scheduled_flow_run_name(flow_run.parameters)
                if flow_run.name == new_name:
                    continue

                await client.set_flow_run_name(flow_run.id, new_name)
                renamed_count += 1

            offset += len(flow_runs)

        if print_summary:
            LOGGER.info("Renamed scheduled flow runs: %s", renamed_count)
        return renamed_count


def scheduled_run_renamer_loop(interval_seconds=30, deployment_name=DEPLOYMENT_NAME):
    while True:
        try:
            renamed_count = asyncio.run(
                rename_scheduled_runs(
                    deployment_name=deployment_name,
                    print_summary=False,
                )
            )
            if renamed_count:
                LOGGER.info("Renamed scheduled flow runs: %s", renamed_count)
        except Exception as exc:
            LOGGER.warning("Erro ao renomear flow runs agendados: %s", exc)
        sleep(interval_seconds)


__all__ = ["DEPLOYMENT_NAME", "rename_scheduled_runs", "scheduled_run_renamer_loop"]
