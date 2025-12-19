"""
Stylizer module for DDCVacuum - Clarity Format
Converts raw records to Clarity's linesContent JSON structure
"""
from utils.styles import description_to_clarity_format


def stylize_records(records: list[dict]) -> list[dict]:
    """
    Convertit une liste de records en ajoutant les descriptions au format Clarity.

    Args:
        records: Liste de dictionnaires avec 'Description'

    Returns:
        Liste de records avec 'descriptions' au format Clarity
    """
    styled = []

    for record in records:
        styled_record = record.copy()

        description = record.get("Description", "")
        if description:
            styled_record["descriptions"] = {
                "en": description_to_clarity_format(description)
            }

        styled.append(styled_record)

    return styled