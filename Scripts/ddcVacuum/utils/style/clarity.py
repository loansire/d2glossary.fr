"""
Clarity format converters

Handles conversion to D2Clarity's specific JSON structure
"""

import re
from typing import Any
from utils.style.processors import text_to_clarity_line


def description_to_clarity_format(description: str, item_name: str = None) -> list[dict[str, Any]]:
    """
    Convert a full description to Clarity's descriptions.en format.

    Args:
        description: Full description text with potential newlines
        item_name: Optional item name for dynamic pattern matching

    Returns:
        Clarity-formatted description structure
    """
    if not description or not isinstance(description, str):
        return []

    result = []
    paragraphs = re.split(r'\n\s*\n|\r\n\s*\r\n', description)

    for i, para in enumerate(paragraphs):
        if not para.strip():
            continue

        lines = para.strip().split('\n')

        for j, line in enumerate(lines):
            line = line.strip()
            if not line:
                continue

            # Passer le nom de l'item pour le pattern dynamique
            line_content = text_to_clarity_line(line, item_name=item_name)
            result.append({"linesContent": line_content})

        if i < len(paragraphs) - 1:
            result.append({"classNames": ["spacer"]})

    return result


def record_to_clarity_format(record: dict, hash_key: str = "Hash") -> dict[str, Any]:
    """
    Convert a DDCVacuum record to Clarity JSON format.

    Input record example:
    {
        "Hash": 12345,
        "Name": "Rampage",
        "Description": "Kills grant damage...",
        "Type": "Weapon Trait"
    }

    Output Clarity format:
    {
        "12345": {
            "hash": 12345,
            "name": "Rampage",
            "type": "Weapon Trait",
            "descriptions": {
                "en": [
                    {"linesContent": [{"text": "Kills grant damage..."}]}
                ]
            }
        }
    }

    Args:
        record: DDCVacuum record dictionary
        hash_key: Field name containing the hash (default: "Hash")

    Returns:
        Clarity-formatted record dictionary
    """
    hash_value = record.get(hash_key, record.get("hash", 0))
    name = record.get("Name", record.get("name", ""))
    description = record.get("Description", record.get("description", ""))
    perk_type = record.get("Type", record.get("type", ""))

    clarity_record = {
        "hash": hash_value,
        "name": name,
        "type": perk_type,
        "descriptions": {
            "en": description_to_clarity_format(description)
        }
    }

    # Add optional fields if present
    if "itemHash" in record:
        clarity_record["itemHash"] = record["itemHash"]
    if "itemName" in record:
        clarity_record["itemName"] = record["itemName"]

    return {str(hash_value): clarity_record}


def records_to_clarity_json(records: list[dict], hash_key: str = "Hash") -> dict[str, Any]:
    """
    Convert a list of records to a full Clarity-compatible JSON structure.

    Args:
        records: List of DDCVacuum records
        hash_key: Field name containing the hash (default: "Hash")

    Returns:
        Dictionary with hash keys mapping to Clarity records

    Example:
        >>> records = [
        ...     {"Hash": 1, "Name": "Test", "Description": "Text"},
        ...     {"Hash": 2, "Name": "Test2", "Description": "Text2"}
        ... ]
        >>> clarity_json = records_to_clarity_json(records)
        >>> print(list(clarity_json.keys()))
        ['1', '2']
    """
    result = {}

    for record in records:
        clarity_record = record_to_clarity_format(record, hash_key)
        result.update(clarity_record)

    return result


# =============================================================================
# UTILITY FUNCTIONS
# =============================================================================

def add_link(text: str, url: str) -> dict[str, Any]:
    """
    Create a link segment in Clarity format

    Args:
        text: Link text
        url: Link URL

    Returns:
        Clarity link segment
    """
    return {
        "text": text,
        "link": url,
        "classNames": ["link"]
    }


def add_tooltip(text: str, tooltip_content: list[dict]) -> dict[str, Any]:
    """
    Create a tooltip segment in Clarity format

    Args:
        text: Tooltip trigger text
        tooltip_content: Tooltip content (Clarity format)

    Returns:
        Clarity tooltip segment
    """
    return {
        "text": text,
        "title": tooltip_content,
        "classNames": ["title"]
    }


def create_spacer() -> dict[str, Any]:
    """
    Create a spacer element

    Returns:
        Clarity spacer element
    """
    return {"classNames": ["spacer"]}