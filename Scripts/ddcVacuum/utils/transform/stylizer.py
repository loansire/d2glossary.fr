"""
Stylizer module for DDCVacuum - DDCVacuum Format
Converts raw records to DDCVacuum's linesContent JSON structure
"""

from utils.style.ddcvacuum import description_to_ddcvacuum_format


def stylize_records(records: list[dict]) -> list[dict]:
    """
    Convertit une liste de records en ajoutant les descriptions au format DDCVacuum.
    """
    styled = []

    for record in records:
        styled_record = record.copy()
        description = record.get("Description", "")
        item_name = record.get("Name", "")  # Récupérer le nom

        if description:
            # Passer le nom de l'item pour le pattern dynamique
            styled_record["descriptions"] = {
                "en": description_to_ddcvacuum_format(description, item_name=item_name)
            }

        styled.append(styled_record)

    return styled