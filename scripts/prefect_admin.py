import argparse
from datetime import timedelta

from prefect.automations import Automation, EventTrigger, Posture, RunDeployment
from prefect.client.orchestration import get_client
from prefect.client.schemas.filters import (
    FlowRunFilter,
    FlowRunFilterDeploymentId,
    FlowRunFilterState,
    FlowRunFilterStateType,
)
from prefect.client.schemas.objects import StateType

from core.prefect_support.deployment_names import (
    SCHEDULED_TREATMENT_QUALIFIED_DEPLOYMENT_NAME,
)
from core.ingest.diagnostics import (
    diagnose_ingest_theme,
    format_ingest_theme_diagnostic,
)
from core.prefect_support.bootstrap import (
    bootstrap_prefect as run_bootstrap_prefect,
    set_default_blocks,
    set_default_variables,
    set_default_work_pools,
)
DOWNLOAD_AUTOMATION_NAME = "Dataset baixado -> tratamento de dados"
DOWNLOAD_AUTOMATION_OLD_NAMES = ("CAR baixado -> tratamento de dados",)
TREATMENT_DEPLOYMENT_CANDIDATES = (
    SCHEDULED_TREATMENT_QUALIFIED_DEPLOYMENT_NAME,
)


def main():
    parser = argparse.ArgumentParser(description="Administracao local do Prefect.")
    subparsers = parser.add_subparsers(dest="command", required=True)

    subparsers.add_parser(
        "create-download-automation",
        help="Cria ou atualiza a automation dataset.downloaded -> tratamento.",
    )
    subparsers.add_parser(
        "create-car-download-automation",
        help="Alias legado de create-download-automation.",
    )
    subparsers.add_parser(
        "rename-scheduled-runs",
        help="Renomeia runs agendados para o theme_folder.",
    )
    subparsers.add_parser(
        "set-default-variables",
        help="Grava as Variables padrao usadas pelos flows.",
    )
    subparsers.add_parser(
        "set-default-blocks",
        help="Grava os Blocks padrao usados pelos flows.",
    )
    subparsers.add_parser(
        "set-default-work-pools",
        help="Cria ou atualiza os Work Pools padrao.",
    )
    subparsers.add_parser(
        "bootstrap-prefect",
        help="Recria Variables, Blocks, Work Pools e Automations padrao.",
    )
    diagnose_parser = subparsers.add_parser(
        "diagnose-theme",
        help="Mostra por que um theme_folder entra ou nao na fila.",
    )
    diagnose_parser.add_argument("theme_folder")

    args = parser.parse_args()
    if args.command in {"create-download-automation", "create-car-download-automation"}:
        create_download_automation()
    elif args.command == "rename-scheduled-runs":
        rename_scheduled_runs()
    elif args.command == "set-default-variables":
        set_default_variables()
    elif args.command == "set-default-blocks":
        set_default_blocks()
    elif args.command == "set-default-work-pools":
        set_default_work_pools()
    elif args.command == "bootstrap-prefect":
        bootstrap_prefect()
    elif args.command == "diagnose-theme":
        diagnose_theme(args.theme_folder)


def create_download_automation():
    with get_client(sync_client=True) as client:
        deployment = read_first_existing_deployment(client, TREATMENT_DEPLOYMENT_CANDIDATES)

    automation = Automation(
        name=DOWNLOAD_AUTOMATION_NAME,
        description=(
            "Quando o flow de download emitir dataset.downloaded, executa o "
            "deployment de tratamento para o dataset baixado."
        ),
        enabled=True,
        tags=["download", "tratamento"],
        trigger=EventTrigger(
            expect={"dataset.downloaded"},
            posture=Posture.Reactive,
            threshold=1,
            within=timedelta(seconds=10),
        ),
        actions=[
            RunDeployment(
                deployment_id=deployment.id,
                parameters={
                    "theme_folders": "{{ event.payload.theme_folders }}",
                    "source_path_overrides": "{{ event.payload.source_path_overrides }}",
                },
            )
        ],
    )

    try:
        existing = read_existing_automation(
            (DOWNLOAD_AUTOMATION_NAME, *DOWNLOAD_AUTOMATION_OLD_NAMES)
        )
    except ValueError:
        created = automation.create()
        print(f"Automation criada: {created.name} ({created.id})")
        return

    automation.id = existing.id
    automation.update()
    print(f"Automation atualizada: {automation.name} ({automation.id})")


def read_existing_automation(names):
    for name in names:
        try:
            return Automation.read(name=name)
        except ValueError:
            pass
    raise ValueError("Automation nao encontrada")


def bootstrap_prefect():
    run_bootstrap_prefect(create_download_automation)


def diagnose_theme(theme_folder):
    diagnostic = diagnose_ingest_theme(theme_folder)
    for line in format_ingest_theme_diagnostic(diagnostic):
        print(line)


def rename_scheduled_runs():
    with get_client(sync_client=True) as client:
        deployment = read_first_existing_deployment(client, TREATMENT_DEPLOYMENT_CANDIDATES)
        scheduled_runs = read_scheduled_runs(client, deployment.id)
        renamed = 0
        for flow_run in scheduled_runs:
            theme_folders = (flow_run.parameters or {}).get("theme_folders") or []
            if len(theme_folders) != 1:
                continue
            client.set_flow_run_name(flow_run.id, theme_folders[0])
            renamed += 1
    print(f"Runs agendados renomeados: {renamed}")


def read_first_existing_deployment(client, deployment_names):
    errors = []
    for deployment_name in deployment_names:
        try:
            return client.read_deployment_by_name(deployment_name)
        except Exception as exc:
            errors.append(f"{deployment_name}: {exc}")
    raise RuntimeError(
        "Nenhum deployment esperado foi encontrado. Tentativas: "
        + " | ".join(errors)
    )


def read_scheduled_runs(client, deployment_id):
    return client.read_flow_runs(
        flow_run_filter=FlowRunFilter(
            deployment_id=FlowRunFilterDeploymentId(any_=[deployment_id]),
            state=FlowRunFilterState(
                type=FlowRunFilterStateType(any_=[StateType.SCHEDULED])
            ),
        ),
        limit=200,
    )


if __name__ == "__main__":
    main()
