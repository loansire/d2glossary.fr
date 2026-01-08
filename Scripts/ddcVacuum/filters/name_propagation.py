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
            current_name = record.get(self.name_field)

            # Gérer les cas None, NaN (float), et chaînes vides
            is_empty = (
                current_name is None or
                (isinstance(current_name, float) and str(current_name).lower() == "nan") or
                (isinstance(current_name, str) and not current_name.strip())
            )

            # Si le Name est vide ou NaN, utiliser le dernier Name valide
            if is_empty:
                if last_valid_name:
                    record = record.copy()
                    record[self.name_field] = last_valid_name
            else:
                # Mettre à jour le dernier Name valide (convertir en string si nécessaire)
                last_valid_name = str(current_name).strip() if not isinstance(current_name, str) else current_name.strip()

            processed.append(record)

        return processed