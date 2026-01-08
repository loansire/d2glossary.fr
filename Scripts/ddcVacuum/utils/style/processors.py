"""
Text processors for style pattern application

Handles text segmentation and CSS class application based on patterns
"""

import re
from typing import Any
from utils.style.patterns import STYLE_PATTERNS, STYLES_ORDER


def text_to_clarity_line(text: str, item_name: str = None) -> list[dict[str, Any]]:
    """
    Convert a text string to Clarity's linesContent format.
    Returns a list of segments with text and optional classNames.

    Args:
        text: Text string to process
        item_name: Optional item name for dynamic pattern matching

    Returns:
        List of text segments with optional CSS classes
    """
    if not text or not isinstance(text, str):
        return [{"text": str(text) if text else ""}]

    segments = []
    current_pos = 0
    matches = []

    # Collect all matches with their positions
    for style_name in STYLES_ORDER:
        config = STYLE_PATTERNS.get(style_name)
        if not config:
            continue

        # Gérer les patterns dynamiques
        if config.get("dynamic") and style_name == "perk_name_reference":
            if not item_name:
                continue  # Skip si pas de nom d'item fourni

            # Créer le pattern dynamiquement en échappant les caractères spéciaux
            escaped_name = re.escape(item_name)
            pattern = rf'\b{escaped_name}\b'
        else:
            pattern = config["pattern"]

        css_class = config["class"]
        flags = config.get("flags", 0)

        for match in re.finditer(pattern, text, flags):
            capture_group = config.get("capture_group", 0)
            start, end = match.span(capture_group) if capture_group else match.span()
            matched_text = match.group(capture_group) if capture_group else match.group()

            matches.append({
                "start": start,
                "end": end,
                "text": matched_text,
                "class": css_class,
                "full_match": match.group(0),
                "full_start": match.start(),
                "full_end": match.end()
            })

    # Sort by position and remove overlaps (keep first match)
    matches.sort(key=lambda x: (x["start"], -x["end"]))
    filtered_matches = []
    last_end = 0

    for m in matches:
        if m["start"] >= last_end:
            filtered_matches.append(m)
            last_end = m["end"]

    # Build segments
    for m in filtered_matches:
        # Add plain text before this match
        if m["start"] > current_pos:
            plain_text = text[current_pos:m["start"]]
            if plain_text:
                segments.append({"text": plain_text})

        # Add styled segment
        segment = {"text": m["text"]}
        if m["class"]:
            segment["classNames"] = [m["class"]]
        segments.append(segment)

        current_pos = m["end"]

    # Add remaining text
    if current_pos < len(text):
        remaining = text[current_pos:]
        if remaining:
            segments.append({"text": remaining})

    # If no segments created, return the original text
    if not segments:
        return [{"text": text}]

    return segments