import re
from utils.styles import STYLES_CONFIG, STYLES_ORDER


def stylize_text(text: str) -> str:
    """Applique les styles HTML au texte"""
    if not isinstance(text, str):
        return text

    for style_name in STYLES_ORDER:
        config = STYLES_CONFIG[style_name]
        pattern = config["pattern"]
        flags = config.get("flags", 0)

        if "replacement" in config:
            text = re.sub(pattern, config["replacement"], text, flags=flags)
        elif config.get("class"):
            css_class = config["class"]
            text = re.sub(
                pattern,
                rf'<span class="{css_class}">\1</span>',
                text,
                flags=flags
            )

    return text


def stylize_records(records: list[dict]) -> list[dict]:
    """Applique les styles à tous les enregistrements"""
    styled = []

    for record in records:
        styled_record = {}
        for key, value in record.items():
            if isinstance(value, str):
                styled_record[key] = stylize_text(value)
            else:
                styled_record[key] = value
        styled.append(styled_record)

    return styled