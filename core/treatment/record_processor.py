from core.treatment.result import TreatmentRecordResult
from core.treatment.service import TreatmentService


def process_treatment_record(
    record,
    output_dir,
    id_start=1,
    use_configured_final_name=False,
    persist_individual_output=True,
):
    service = TreatmentService()
    return service.process(
        record,
        output_dir,
        id_start=id_start,
        use_configured_final_name=use_configured_final_name,
        persist_individual_output=persist_individual_output,
    )


__all__ = ["TreatmentRecordResult", "process_treatment_record"]
