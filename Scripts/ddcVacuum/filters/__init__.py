"""
Système de filtres pour DDCVacuum
Permet d'appliquer des transformations spécifiques à chaque sheet
"""

from typing import Any


class BaseFilter:
    """Classe de base pour tous les filtres"""

    def __init__(self, config: dict[str, Any] = None):
        """
        Initialise le filtre avec une configuration optionnelle

        Args:
            config: Configuration spécifique au filtre
        """
        self.config = config or {}

    def apply(self, records: list[dict]) -> list[dict]:
        """
        Applique le filtre sur une liste de records

        Args:
            records: Liste des enregistrements à filtrer

        Returns:
            Liste des enregistrements filtrés
        """
        raise NotImplementedError("Les filtres doivent implémenter la méthode apply()")

    def process_record(self, record: dict, context: dict = None) -> dict:
        """
        Traite un enregistrement individuel

        Args:
            record: L'enregistrement à traiter
            context: Contexte additionnel (ex: enregistrement précédent)

        Returns:
            L'enregistrement traité
        """
        return record