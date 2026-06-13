def clean_for_voice(text):
    if not text:
        return ""

    cleaned = text

    remove_chars = [
        "=", "-", "*", "[", "]", "(", ")", "{", "}",
        "#", "_", "`", "|"
    ]

    for ch in remove_chars:
        cleaned = cleaned.replace(ch, " ")

    cleaned = cleaned.replace(":", "은")
    cleaned = cleaned.replace("/", " 또는 ")

    while "  " in cleaned:
        cleaned = cleaned.replace("  ", " ")

    return cleaned.strip()