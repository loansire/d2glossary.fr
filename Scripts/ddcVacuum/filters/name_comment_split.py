"""
Filtre de séparation Name/Comment
Gère la décomposition des champs Name qui contiennent des retours à la ligne
Pattern: NAME\n\nCOMMENT (où COMMENT peut contenir des \n)
Exemple: "Collective Psyche\n\nRaid\nPerpetual Desert"
"""

import re
from filters import BaseFilter


class NameCommentSplitFilter(BaseFilter):
    """
    Décompose le champ Name en extrayant le Comment si présent
    Pattern détecté:
    - Première partie = Name (jusqu'au premier \n)
    - Reste = Comment (peut contenir des \n multiples)
    Exemple: "Name\n\nComment line 1\nComment line 2"
    """

    def __init__(self, config: dict = None):
        super().__init__(config)
        self.name_field = self.config.get("name_field", "Name")
        self.comment_field = self.config.get("comment_field", "Comment")

    def apply(self, records: list[dict]) -> list[dict]:
        """
        Traite tous les records pour séparer Name et Comment

        Args:
            records: Liste des enregistrements

        Returns:
            Liste des enregistrements avec Name et Comment séparés
        """
        processed = []

        for record in records:
            processed_record = self.process_record(record)
            processed.append(processed_record)

        return processed

    def process_record(self, record: dict, context: dict = None) -> dict:
        """
        Traite un enregistrement pour extraire le Comment du Name

        Pattern: "Name\n\nComment" où Comment peut contenir des \n
        Exemple: "Collective Psyche\n\nRaid\nPerpetual Desert"
        -> Name="Collective Psyche", Comment="Raid\nPerpetual Desert"

        Args:
            record: L'enregistrement à traiter
            context: Non utilisé ici

        Returns:
            L'enregistrement avec Name et Comment séparés
        """
        name_value = record.get(self.name_field, "")

        if not name_value or not isinstance(name_value, str):
            return record

        # Vérifier s'il y a des retours à la ligne
        if "\n" not in name_value:
            return record

        # Créer une copie pour ne pas modifier l'original
        record = record.copy()

        # Pattern: Première ligne = Name, tout le reste = Comment
        # Chercher le premier \n (peut être suivi d'autres \n)
        first_newline = name_value.find("\n")

        if first_newline != -1:
            # Extraire le Name (avant le premier \n)
            name = name_value[:first_newline].strip()

            # Extraire le Comment (tout après le premier \n)
            # On enlève les \n initiaux mais on garde les \n internes
            comment = name_value[first_newline:].lstrip("\n").rstrip()

            # Assigner les valeurs
            record[self.name_field] = name

            if comment:  # Seulement si le comment n'est pas vide
                record[self.comment_field] = comment

        return record

    def extract_name_comment_pattern(self, text: str) -> tuple[str, str]:
        """
        Méthode alternative pour des patterns plus complexes si nécessaire

        Args:
            text: Le texte à analyser

        Returns:
            Tuple (name, comment)
        """
        # Chercher le premier \n
        first_newline = text.find("\n")

        if first_newline == -1:
            # Pas de \n trouvé
            return text.strip(), ""

        # Séparer au premier \n
        name = text[:first_newline].strip()
        comment = text[first_newline:].lstrip("\n").rstrip()

        return name, comment