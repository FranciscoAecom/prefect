__all__ = [
    "TreatmentRunContext",
    "TreatmentService",
    "load_treatment_records",
    "prepare_treatment_run",
    "process_treatment_record",
    "run_data_treatment",
    "run_treatment_record",
]


def __getattr__(name):
    if name == "process_treatment_record":
        from core.treatment.record_processor import process_treatment_record

        return process_treatment_record
    if name in {
        "TreatmentRunContext",
        "load_treatment_records",
        "prepare_treatment_run",
    }:
        from core.ingest.loader import load_treatment_records
        from core.treatment.run_loader import TreatmentRunContext, prepare_treatment_run

        return {
            "TreatmentRunContext": TreatmentRunContext,
            "load_treatment_records": load_treatment_records,
            "prepare_treatment_run": prepare_treatment_run,
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
