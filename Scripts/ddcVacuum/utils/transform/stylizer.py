"""
Stylizer module for DDCVacuum - Clarity Format
Converts raw records to Clarity's linesContent JSON structure
"""

from utils.style.clarity import description_to_clarity_format


def stylize_records(records: list[dict]) -> list[dict]:
    """
    Convertit une liste de records en ajoutant les descriptions au format Clarity.

    Ajoute un champ 'descriptions' avec le format Clarity pour chaque record
    qui contient une 'Description'.

    Args:
        records: Liste de dictionnaires avec 'Description'

    Returns:
        Liste de records avec 'descriptions' au format Clarity

    Example:
        >>> records = [{"Name": "Test", "Description": "Simple text"}]
        >>> styled = stylize_records(records)
        >>> print(styled[0]["descriptions"]["en"])
        [{"linesContent": [{"text": "Simple text"}]}]
    """
    styled = []

    for record in records:
        # Copier le record pour ne pas modifier l'original
        styled_record = record.copy()

        # Récupérer la description
        description = record.get("Description", "")

        # Si une description existe, ajouter le format Clarity
        if description:
            styled_record["descriptions"] = {
                "en": description_to_clarity_format(description)
            }

        styled.append(styled_record)

    return styled