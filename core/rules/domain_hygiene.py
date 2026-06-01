BROKEN_DASH_SEPARATOR = chr(0x00BF)
MOJIBAKE_LEAD_CHARS = ("Ã", "Â", "Ă")


def _mojibake_score(value):
    text = str(value or "")
    return sum(0x80 <= ord(char) <= 0x9F for char in text) + sum(
        lead in MOJIBAKE_LEAD_CHARS and 0x80 <= ord(char) <= 0xBF
        for lead, char in zip(text, text[1:])
    ) + text.count("â€")


def looks_like_mojibake(value):
    return _mojibake_score(value) > 0


def repair_utf8_mojibake(value):
    original = str(value or "")
    repaired = original

    for _ in range(2):
        current_score = _mojibake_score(repaired)
        if not current_score:
            break

        candidates = []
        for source_encoding in ("latin-1", "cp1252"):
            try:
                candidate = repaired.encode(source_encoding).decode("utf-8")
            except (UnicodeEncodeError, UnicodeDecodeError):
                continue
            if _mojibake_score(candidate) < current_score:
                candidates.append(candidate)

        if not candidates:
            break
        repaired = min(candidates, key=lambda candidate: (_mojibake_score(candidate), len(candidate)))

    if repaired != original and not looks_like_mojibake(repaired):
        return repaired
    return None


def canonicalize_domain_text(value):
    if value is None:
        return ""
    text = str(value).strip()
    text = text.replace(BROKEN_DASH_SEPARATOR, "-")
    text = text.replace(" ? ", " - ")
    return " ".join(text.split())


def build_accepted_values_and_aliases(values):
    accepted_values = []
    aliases = {}
    mojibake_values = []

    for value in unique_text_values(values):
        if looks_like_mojibake(value):
            mojibake_values.append(value)
            continue

        canonical = canonicalize_domain_text(value)
        if not canonical:
            continue
        accepted_values.append(canonical)
        if canonical != value:
            aliases[value] = canonical

    for value in mojibake_values:
        repaired = repair_utf8_mojibake(value)
        canonical = canonicalize_domain_text(repaired)
        if canonical:
            accepted_values.append(canonical)
            aliases[value] = canonical

    return (
        sorted(dict.fromkeys(accepted_values), key=str),
        dict(sorted(aliases.items())),
    )


def unique_text_values(values):
    seen = {}
    for value in values:
        if value is None:
            continue
        text = str(value).strip()
        if not text:
            continue
        seen.setdefault(text, None)
    return list(seen)


__all__ = [
    "BROKEN_DASH_SEPARATOR",
    "build_accepted_values_and_aliases",
    "canonicalize_domain_text",
    "looks_like_mojibake",
    "repair_utf8_mojibake",
    "unique_text_values",
]
