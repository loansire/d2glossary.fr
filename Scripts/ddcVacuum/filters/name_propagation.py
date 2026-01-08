"""
Filtre de propagation du champ Name
Utilisé pour ArmorSets où certains enregistrements n'ont pas de Name
et doivent hériter du Name de l'enregistrement précédent
"""

from filters import BaseFilter


class NamePropagationFilter(BaseFilter):
    """
    Propage le champ Name des enregistrements précédents
    vers les enregistrements qui ont un Name vide
    """

    def __init__(self, config: dict = None):
        super().__init__(config)
        self.name_field = self.config.get("name_field", "Name")

    def apply(self, records: list[dict]) -> list[dict]:
        """
        Parcourt les records et propage le Name si nécessaire

        Args:
            records: Liste des enregistrements

        Returns:
            Liste des enregistrements avec Names propagés
        """
        if not records:
            return records

        processed = []
        last_valid_name = None

        for record in records:
            current_name = record.get(self.name_field, "").strip()

            # Si le Name est vide ou NaN, utiliser le dernier Name valide
            if not current_name or str(current_name).lower() == "nan":
                if last_valid_name:
                    record = record.copy()
                    record[self.name_field] = last_valid_name
            else:
                # Mettre à jour le dernier Name valide
                last_valid_name = current_name

            processed.append(record)

        return processed