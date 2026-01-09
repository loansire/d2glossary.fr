"""
Text processors for style pattern application

Handles text segmentation and CSS class application based on patterns
"""

import re
from typing import Any
from utils.style.patterns import STYLE_PATTERNS, STYLES_ORDER


def text_to_ddcvacuum_line(text: str, item_name: str = None) -> list[dict[str, Any]]:
    """
    Convert a text string to DDCVacuum's linesContent format.
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

    # Track already matched regions to prevent overlaps
    matched_regions = []  # List of (start, end) tuples

    def is_overlapping(start, end):
        """Check if a region overlaps with any already matched region"""
        for region_start, region_end in matched_regions:
            # Check for any overlap
            if not (end <= region_start or start >= region_end):
                return True
        return False

    def add_matched_region(start, end):
        """Add a new matched region and merge overlapping ones"""
        matched_regions.append((start, end))
        # Keep regions sorted for efficient checking
        matched_regions.sort()

    # Collect all matches with their positions, respecting priority order
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

            # Skip this match if it overlaps with already matched regions
            if is_overlapping(start, end):
                continue

            # Add this match and mark the region as matched
            matches.append({
                "start": start,
                "end": end,
                "text": matched_text,
                "class": css_class,
                "full_match": match.group(0),
                "full_start": match.start(),
                "full_end": match.end()
            })
            add_matched_region(start, end)

    # Sort matches by position for segment building
    matches.sort(key=lambda x: x["start"])
    filtered_matches = matches  # No need for additional filtering now

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