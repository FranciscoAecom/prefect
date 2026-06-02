from collections import Counter

from core.utils import log
from core.validation.session import validation_session_or_default


def field_summary_entry(column, validation_session=None):
    validation_session = validation_session_or_default(validation_session)
    return validation_session.summary["fields"].setdefault(
        column,
        {
            "status_counts": Counter(),
            "reason_counts": Counter(),
        },
    )


def register_domain_validation_summary(column, statuses, reasons, validation_session=None):
    entry = field_summary_entry(column, validation_session=validation_session)
    entry["status_counts"].update(statuses)
    entry["reason_counts"].update(
        reason for status, reason in zip(statuses, reasons)
        if status in {"invalid", "empty"} and reason
    )


def relation_summary_entry(relation_key, validation_session=None):
    validation_session = validation_session_or_default(validation_session)
    return validation_session.summary["relations"].setdefault(
        relation_key,
        {
            "status_counts": Counter(),
            "reason_counts": Counter(),
            "autocorrected_counts": Counter(),
            "unchecked_source_counts": Counter(),
            "relation_map": {},
        },
    )


def log_validation_summary(validation_session=None):
    validation_session = validation_session_or_default(validation_session)
    for column, entry in validation_session.summary["fields"].items():
        status_counts = entry["status_counts"]
        parts = _count_parts(
            status_counts,
            (
                ("normalized", "normalizado(s) por alias"),
                ("invalid", "invalido(s)"),
                ("empty", "vazio(s)"),
            ),
        )
        if not parts:
            continue

        log(f"Resumo validacao {column}: {', '.join(parts)}")
        _log_counter(entry["reason_counts"], limit=5)

    for relation_key, consistency in validation_session.summary["relations"].items():
        status_counts = consistency["status_counts"]
        parts = _count_parts(
            status_counts,
            (
                ("autocorrected", f"autocorrigido(s) pela relacao {relation_key}"),
                ("inconsistent", "inconsistente(s)"),
                ("unchecked", "nao verificado(s)"),
            ),
        )
        if not parts:
            continue

        log(f"Resumo consistencia relacao {relation_key}: {', '.join(parts)}")

        relation_map = consistency.get("relation_map", {})
        for source_value, count in consistency["autocorrected_counts"].most_common(5):
            expected_target = relation_map.get(source_value)
            if expected_target:
                log(f"  {count}x - Valor ajustado automaticamente para {source_value}: {expected_target}")
        if status_counts.get("unchecked", 0):
            for source_value, count in consistency["unchecked_source_counts"].most_common(10):
                log(f"  {count}x - Valor fonte fora do dominio configurado: {source_value}")
        _log_counter(consistency["reason_counts"], limit=5)


def _count_parts(counts, labels):
    return [
        f"{counts.get(key, 0)} {label}"
        for key, label in labels
        if counts.get(key, 0)
    ]


def _log_counter(counter, limit):
    for reason, count in counter.most_common(limit):
        log(f"  {count}x - {reason}")


__all__ = [
    "field_summary_entry",
    "log_validation_summary",
    "register_domain_validation_summary",
    "relation_summary_entry",
]
