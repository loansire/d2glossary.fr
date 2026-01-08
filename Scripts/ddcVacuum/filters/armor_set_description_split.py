"""
Filtre de décomposition des descriptions d'Armor Sets
Extrait la première ligne et sépare PieceRequirement | Effect
Réorganise les champs: Effect remplace Name, Name devient SetName
"""

import re
from filters import BaseFilter


class ArmorSetDescriptionSplitFilter(BaseFilter):
    """
    Traite les descriptions d'Armor Sets pour extraire:
    - La première ligne du format "X Piece | Effect Name"
    - Sépare en PieceRequirement et Effect
    - Réorganise: Effect → Name, ancien Name → SetName

    Exemple:
    Input:
        Name: "Disaster Corps"
        Description: "2 Piece | Pleas Heard\n\nUpon finishing an Auto Rifle..."

    Output:
        SetName: "Disaster Corps"
        Name: "Pleas Heard"
        PieceRequirement: "2 Piece"
        Description: "Upon finishing an Auto Rifle..."
    """

    def __init__(self, config: dict = None):
        super().__init__(config)
        self.name_field = self.config.get("name_field", "Name")
        self.description_field = self.config.get("description_field", "Description")
        self.set_name_field = self.config.get("set_name_field", "SetName")
        self.piece_requirement_field = self.config.get("piece_requirement_field", "PieceRequirement")

    def apply(self, records: list[dict]) -> list[dict]:
        """
        Traite tous les records d'Armor Sets

        Args:
            records: Liste des enregistrements

        Returns:
            Liste des enregistrements transformés
        """
        processed = []

        for record in records:
            processed_record = self.process_record(record)
            processed.append(processed_record)

        return processed

    def process_record(self, record: dict, context: dict = None) -> dict:
        """
        Traite un enregistrement d'Armor Set

        Pattern détecté: "X Piece | Effect Name\n\nReste de la description"

        Args:
            record: L'enregistrement à traiter
            context: Non utilisé

        Returns:
            L'enregistrement transformé avec les nouveaux champs
        """
        description = record.get(self.description_field, "")
        original_name = record.get(self.name_field, "")

        # Si pas de description ou mauvais type, retourner tel quel
        if not description or not isinstance(description, str):
            return record

        # Si pas de retour à la ligne, pas de traitement possible
        if "\n" not in description:
            return record

        # Créer une copie pour ne pas modifier l'original
        record = record.copy()

        # Extraire la première ligne
        first_line = description.split("\n")[0].strip()

        # Vérifier le pattern "X Piece | Effect"
        # Pattern: nombre/texte + "Piece" + "|" + nom de l'effet
        match = re.match(r'^(.+?\s+Piece)\s*\|\s*(.+)$', first_line, re.IGNORECASE)

        if not match:
            # Si le pattern ne correspond pas, ne rien faire
            return record

        piece_requirement = match.group(1).strip()
        effect_name = match.group(2).strip()

        # Extraire le reste de la description (après la première ligne et les \n)
        # On cherche le premier \n\n pour séparer l'en-tête du corps
        split_pattern = "\n\n"
        if split_pattern in description:
            remaining_description = description.split(split_pattern, 1)[1].strip()
        else:
            # Si pas de \n\n, prendre tout après la première ligne
            lines = description.split("\n")
            remaining_description = "\n".join(lines[1:]).strip() if len(lines) > 1 else ""

        # Réorganiser les champs
        record[self.set_name_field] = original_name  # Ancien Name → SetName
        record[self.name_field] = effect_name  # Effect → Name
        record[self.piece_requirement_field] = piece_requirement  # Nouveau champ
        record[self.description_field] = remaining_description  # Description nettoyée

        return record