from contextlib import ExitStack

from core.execution_locks import named_execution_lock
from core.ingest.run_request import IngestRunRequest
from core.treatment.steps.errors import log_processing_error
from core.treatment.steps.events import emit_project_resolved_event, emit_record_start_events
from core.rules.autofix_service import RuleAutofixService
from core.treatment.context_factory import build_treatment_context
from core.treatment.group_state import QueueGroupState
from core.treatment.result import treatment_failure_result, treatment_success_result
from core.treatment.settings import QueueRunSettings
from core.treatment.steps_runner import run_treatment_steps
from core.utils import log


class TreatmentService:
    def __init__(self, autofix_service=None):
        self.autofix_service = autofix_service or RuleAutofixService()

    def _failure_result(self):
        return treatment_failure_result()

    def process(
        self,
        record,
        output_dir,
        id_start=1,
        use_configured_final_name=False,
        persist_individual_output=True,
    ):
        emit_record_start_events(record)

        try:
            context = build_treatment_context(record, output_dir, id_start=id_start)
        except Exception as exc:
            log_processing_error("Erro ao resolver configuracao do projeto", exc)
            return self._failure_result()

        emit_project_resolved_event(context)

        context = run_treatment_steps(
            context,
            self.autofix_service,
            use_configured_final_name=use_configured_final_name,
            persist_individual_output=persist_individual_output,
        )
        if context is None:
            return self._failure_result()

        return treatment_success_result(context)


def run_data_treatment(output_base=None, theme_folders=None, source_path_overrides=None, force=False):
    from core.tasks.treatment import prepare_treatment_queue_task, run_treatment_record_task

    settings = QueueRunSettings.from_output_base(output_base)
    run_request = IngestRunRequest.from_legacy(
        theme_folders=theme_folders,
        source_path_overrides=source_path_overrides,
        force=force,
    )
    queue_filter = run_request.queue_filter

    with _queue_filter_locks(queue_filter):
        queue_context = prepare_treatment_queue_task(
            settings.output_base,
            theme_folders,
            source_path_overrides,
            force,
        )
        if queue_context is None:
            return

        group_state = QueueGroupState(
            queue_context.records,
            enable_group_consolidation=settings.enable_group_consolidation,
        )

        for record in queue_context.records:
            run_treatment_record_task(
                record,
                queue_context.output_dir,
                group_state,
                settings.keep_individual_outputs_when_grouping,
            )

        log("Tratamento finalizado")


def _queue_filter_locks(queue_filter):
    stack = ExitStack()
    for theme_folder in sorted(queue_filter.theme_folders):
        stack.enter_context(named_execution_lock(f"queue-{theme_folder}"))
    return stack


__all__ = ["TreatmentService", "run_data_treatment"]
