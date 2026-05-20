import argparse
from datetime import datetime, timedelta

from prefect.automations import Automation, EventTrigger, Posture, RunDeployment
from prefect.client.orchestration import get_client
from prefect.client.schemas.actions import DeploymentScheduleCreate
from prefect.client.schemas.filters import (
    FlowRunFilter,
    FlowRunFilterDeploymentId,
    FlowRunFilterState,
    FlowRunFilterStateType,
)
from prefect.client.schemas.objects import StateType
from prefect.client.schemas.schedules import RRuleSchedule

from core.prefect_support.deployment_names import (
    UR_CAR_PROCESSING_OLD_QUALIFIED_DEPLOYMENT_NAMES,
    UR_CAR_PROCESSING_QUALIFIED_DEPLOYMENT_NAME,
)
from core.prefect_support.schedules import (
    UR_CAR_SEQUENCE_HOUR,
    UR_CAR_SEQUENCE_MINUTE,
    UR_CAR_SEQUENCE_START_DATE,
    UR_CAR_SEQUENCE_TIMEZONE,
    UR_CAR_THEME_FOLDERS,
)


DOWNLOAD_AUTOMATION_NAME = "Dataset baixado -> tratamento de dados"
DOWNLOAD_AUTOMATION_OLD_NAMES = ("CAR baixado -> tratamento de dados",)
PROCESSING_DEPLOYMENT_CANDIDATES = (
    UR_CAR_PROCESSING_QUALIFIED_DEPLOYMENT_NAME,
    *UR_CAR_PROCESSING_OLD_QUALIFIED_DEPLOYMENT_NAMES,
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
        "reschedule-ur-car-daily-17h",
        help="Recria a agenda diaria de UR CAR as 17:00.",
    )
    subparsers.add_parser(
        "rename-scheduled-runs",
        help="Renomeia runs agendados para o theme_folder.",
    )

    args = parser.parse_args()
    if args.command in {"create-download-automation", "create-car-download-automation"}:
        create_download_automation()
    elif args.command == "reschedule-ur-car-daily-17h":
        reschedule_ur_car_daily_17h()
    elif args.command == "rename-scheduled-runs":
        rename_scheduled_runs()


def create_download_automation():
    with get_client(sync_client=True) as client:
        deployment = read_first_existing_deployment(client, PROCESSING_DEPLOYMENT_CANDIDATES)

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


def reschedule_ur_car_daily_17h():
    with get_client(sync_client=True) as client:
        deployment = read_first_existing_deployment(client, PROCESSING_DEPLOYMENT_CANDIDATES)

        old_schedules = client.read_deployment_schedules(deployment.id)
        for schedule in old_schedules:
            client.delete_deployment_schedule(deployment.id, schedule.id)

        scheduled_runs = read_scheduled_runs(client, deployment.id)
        for flow_run in scheduled_runs:
            client.delete_flow_run(flow_run.id)

        new_schedules = [
            DeploymentScheduleCreate(
                schedule=RRuleSchedule(
                    rrule=build_single_run_rrule(
                        UR_CAR_SEQUENCE_START_DATE + timedelta(days=index)
                    ),
                    timezone=UR_CAR_SEQUENCE_TIMEZONE,
                ),
                active=True,
                max_scheduled_runs=1,
                parameters={"theme_folders": [theme_folder]},
                slug=theme_folder,
            )
            for index, theme_folder in enumerate(UR_CAR_THEME_FOLDERS)
        ]
        created = client.create_deployment_schedules(deployment.id, new_schedules)

    print(f"Deployment: {deployment.name}")
    print(f"Schedules apagados: {len(old_schedules)}")
    print(f"Flow runs scheduled apagados: {len(scheduled_runs)}")
    print(f"Schedules criados: {len(created)}")
    for index, theme_folder in enumerate(UR_CAR_THEME_FOLDERS):
        scheduled_for = UR_CAR_SEQUENCE_START_DATE + timedelta(days=index)
        print(
            f"{scheduled_for.isoformat()} "
            f"{UR_CAR_SEQUENCE_HOUR:02d}:{UR_CAR_SEQUENCE_MINUTE:02d} - "
            f"{theme_folder}"
        )


def rename_scheduled_runs():
    with get_client(sync_client=True) as client:
        deployment = read_first_existing_deployment(client, PROCESSING_DEPLOYMENT_CANDIDATES)
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


def build_single_run_rrule(scheduled_date):
    scheduled_at = datetime(
        scheduled_date.year,
        scheduled_date.month,
        scheduled_date.day,
        UR_CAR_SEQUENCE_HOUR,
        UR_CAR_SEQUENCE_MINUTE,
    )
    return f"DTSTART:{scheduled_at:%Y%m%dT%H%M%S}\nRRULE:FREQ=DAILY;COUNT=1"


if __name__ == "__main__":
    main()
