__all__ = [
    "QueueRunContext",
    "QueueRunSettings",
    "QueueFilter",
    "log_queue_summary",
    "prepare_processing_queue",
    "run_processing_queue",
    "run_queue_record",
]


def __getattr__(name):
    if name == "QueueFilter":
        from core.queue.filters import QueueFilter

        return QueueFilter
    if name in {"QueueRunContext", "prepare_processing_queue"}:
        from core.queue.queue_loader import QueueRunContext, prepare_processing_queue

        return {
            "QueueRunContext": QueueRunContext,
            "prepare_processing_queue": prepare_processing_queue,
        }[name]
    if name == "run_queue_record":
        from core.queue.record_runner import run_queue_record

        return run_queue_record
    if name == "run_processing_queue":
        from core.queue.runner import run_processing_queue

        return run_processing_queue
    if name == "QueueRunSettings":
        from core.queue.settings import QueueRunSettings

        return QueueRunSettings
    if name == "log_queue_summary":
        from core.queue.summary import log_queue_summary

        return log_queue_summary
    raise AttributeError(name)
