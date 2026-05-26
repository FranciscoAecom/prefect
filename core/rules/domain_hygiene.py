BROKEN_DASH_SEPARATOR = chr(0x00BF)


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

    for value in unique_text_values(values):
        canonical = canonicalize_domain_text(value)
        if not canonical:
            continue
        accepted_values.append(canonical)
        if canonical != value:
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
    "unique_text_values",
]
