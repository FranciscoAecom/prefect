__all__ = [
    "TreatmentQueueRunContext",
    "TreatmentService",
    "load_treatment_queue",
    "prepare_treatment_queue",
    "process_treatment_record_by_dataset_kind",
    "run_data_treatment",
    "run_treatment_record",
]


def __getattr__(name):
    if name == "process_treatment_record_by_dataset_kind":
        from core.treatment.dispatcher import process_treatment_record_by_dataset_kind

        return process_treatment_record_by_dataset_kind
    if name in {
        "TreatmentQueueRunContext",
        "load_treatment_queue",
        "prepare_treatment_queue",
    }:
        from core.treatment.queue import (
            TreatmentQueueRunContext,
            load_treatment_queue,
            prepare_treatment_queue,
        )

        return {
            "TreatmentQueueRunContext": TreatmentQueueRunContext,
            "load_treatment_queue": load_treatment_queue,
            "prepare_treatment_queue": prepare_treatment_queue,
        }[name]
    if name == "run_treatment_record":
        from core.treatment.runner import run_treatment_record

        return run_treatment_record
    if name in {"TreatmentService", "run_data_treatment"}:
        from core.treatment.service import TreatmentService, run_data_treatment

        return {
            "TreatmentService": TreatmentService,
            "run_data_treatment": run_data_treatment,
        }[name]
    raise AttributeError(name)
