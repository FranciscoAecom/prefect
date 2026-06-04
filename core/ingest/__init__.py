__all__ = [
    "IngestIssue",
    "IngestRecord",
    "load_treatment_queue",
]


def __getattr__(name):
    if name == "load_treatment_queue":
        from core.ingest.loader import load_treatment_queue

        return load_treatment_queue
    if name in {"IngestIssue", "IngestRecord"}:
        from core.ingest.models import IngestIssue, IngestRecord

        return {"IngestIssue": IngestIssue, "IngestRecord": IngestRecord}[name]
    raise AttributeError(name)
