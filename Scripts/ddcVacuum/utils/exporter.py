import json
from utils.styles import CSS_STYLES


def save_json(data: any, filepath: str) -> None:
    """Sauvegarde des données en JSON"""
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def save_css(filepath: str) -> None:
    """Sauvegarde le CSS"""
    with open(filepath, "w", encoding="utf-8") as f:
        f.write(CSS_STYLES)


def clarity_to_html(clarity_content: list[dict]) -> str:
    """Convertit le format Clarity linesContent en HTML"""
    if not clarity_content:
        return ""

    html_parts = []

    for item in clarity_content:
        if "classNames" in item and "spacer" in item.get("classNames", []):
            html_parts.append('<div class="spacer"></div>')
            continue

        if "linesContent" in item:
            line_html = ""
            for segment in item["linesContent"]:
                text = segment.get("text", "")
                classes = segment.get("classNames", [])
                link = segment.get("link")

                if link:
                    line_html += f'<a href="{link}" class="link" target="_blank">{text}</a>'
                elif classes:
                    class_str = " ".join(classes)
                    line_html += f'<span class="{class_str}">{text}</span>'
                else:
                    line_html += text

            html_parts.append(f'<div class="line">{line_html}</div>')

    return "\n".join(html_parts)


def generate_html(data: dict[str, list[dict]], filepath: str) -> None:
    """Génère une page HTML de prévisualisation"""

    html = f"""<!DOCTYPE html>
<html lang="fr">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>D2 Glossary</title>
    <link rel="stylesheet" href="../../../assets/css/variables.css">
    <link rel="stylesheet" href="../../../assets/css/components.css">
    <link rel="stylesheet" href="../../../assets/css/d2elementstyles.css">
    <style>
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background-color: #1a1a2e;
            color: #eee;
            padding: 20px;
            line-height: 1.6;
        }}
        h1 {{ color: #fff; border-bottom: 2px solid #51cf66; padding-bottom: 10px; }}
        h2 {{ color: #74c0fc; margin-top: 40px; }}
        .nav {{
            position: sticky;
            top: 0;
            background: #1a1a2e;
            padding: 10px 0;
            border-bottom: 1px solid #333;
            margin-bottom: 20px;
            z-index: 100;
        }}
        .nav a {{
            color: #74c0fc;
            margin-right: 15px;
            text-decoration: none;
        }}
        .nav a:hover {{
            color: #51cf66;
            text-decoration: underline;
        }}
        .perk {{
            background: #16213e;
            border-radius: 8px;
            padding: 15px;
            margin: 10px 0;
            border-left: 4px solid #51cf66;
        }}
        .perk-name {{
            font-size: 1.2em;
            font-weight: bold;
            color: #fff;
            margin-bottom: 8px;
        }}
        .perk-description .line {{
            margin: 2px 0;
        }}
        .perk-description .spacer {{
            height: 8px;
        }}
        .count {{
            color: #868e96;
            font-size: 0.9em;
            margin-left: 10px;
        }}
    </style>
</head>
<body>
    <h1>🎮 Destiny 2 Glossary</h1>
    <nav class="nav">
"""

    for sheet_name in data.keys():
        html += f'        <a href="#{sheet_name}">{sheet_name}</a>\n'

    html += "    </nav>\n"

    for sheet_name, records in data.items():
        html += f'    <h2 id="{sheet_name}">{sheet_name}<span class="count">({len(records)} items)</span></h2>\n'

        for record in records:
            name = record.get("Name", "")

            # Utilise le format Clarity
            if "descriptions" in record:
                description_html = clarity_to_html(record["descriptions"].get("en", []))
            else:
                description_html = record.get("Description", "")

            if name or description_html:
                html += f"""    <div class="perk">
        <div class="perk-name">{name if name else "—"}</div>
        <div class="perk-description">{description_html if description_html else "—"}</div>
    </div>
"""

    html += """
</body>
</html>
"""

    with open(filepath, "w", encoding="utf-8") as f:
        f.write(html)