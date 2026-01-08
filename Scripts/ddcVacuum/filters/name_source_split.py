"""
Filtre de séparation Name/Source
Gère la décomposition des champs Name qui contiennent des retours à la ligne
Pattern: name\n ou \n\nsource
"""

import re
from filters import BaseFilter


class NameSourceSplitFilter(BaseFilter):
    """
    Décompose le champ Name en extrayant le source si présent
    Pattern détecté:
    - "name\nsource"
    - "name\n\nsource"
    - "name\n\n\nsource"
    """

    def __init__(self, config: dict = None):
        super().__init__(config)
        self.name_field = self.config.get("name_field", "Name")
        self.source_field = self.config.get("source_field", "source")

    def apply(self, records: list[dict]) -> list[dict]:
        """
        Traite tous les records pour séparer Name et Source

        Args:
            records: Liste des enregistrements

        Returns:
            Liste des enregistrements avec Name et source séparés
        """
        processed = []

        for record in records:
            processed_record = self.process_record(record)
            processed.append(processed_record)

        return processed

    def process_record(self, record: dict, context: dict = None) -> dict:
        """
        Traite un enregistrement pour extraire le source du Name

        Args:
            record: L'enregistrement à traiter
            context: Non utilisé ici

        Returns:
            L'enregistrement avec Name et source séparés
        """
        name_value = record.get(self.name_field, "")

        if not name_value or not isinstance(name_value, str):
            return record

        # Vérifier s'il y a des retours à la ligne
        if "\n" not in name_value:
            return record

        # Créer une copie pour ne pas modifier l'original
        record = record.copy()

        # Pattern: extraire la première ligne comme name
        # et la dernière section (après plusieurs \n) comme source
        parts = name_value.split("\n")

        # Filtrer les parties vides
        non_empty_parts = [p.strip() for p in parts if p.strip()]

        if len(non_empty_parts) >= 2:
            # Le premier élément est le name
            record[self.name_field] = non_empty_parts[0]

            # Le dernier élément est le source
            record[self.source_field] = non_empty_parts[-1]
        elif len(non_empty_parts) == 1:
            # Si une seule partie non vide, c'est le name
            record[self.name_field] = non_empty_parts[0]

        return record

    def extract_source_pattern(self, text: str) -> tuple[str, str]:
        """
        Méthode alternative pour des patterns plus complexes

        Args:
            text: Le texte à analyser

        Returns:
            Tuple (name, source)
        """
        # Pattern plus robuste si nécessaire
        # Ex: "Name\n\nSource" ou "Name\nSource"

        # Chercher un pattern avec plusieurs \n consécutifs
        match = re.match(r"^(.*?)\n{2,}(.+)$", text, re.DOTALL)
        if match:
            return match.group(1).strip(), match.group(2).strip()

        # Sinon, chercher un seul \n
        match = re.match(r"^(.*?)\n(.+)$", text, re.DOTALL)
        if match:
            return match.group(1).strip(), match.group(2).strip()

        # Pas de séparation trouvée
        return text.strip(), ""