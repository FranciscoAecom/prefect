def style_value(style, *keys):
    for key in keys:
        value = style.get(key)
        if value is not None and str(value).strip():
            return str(value)
    return ""
