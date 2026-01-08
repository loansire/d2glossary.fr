"""
Pipeline d'exécution des filtres
Applique séquentiellement les filtres configurés pour une sheet
"""

from typing import Any
from filters.config import get_filters_for_sheet, has_filters


class FilterPipeline:
    """
    Gère l'exécution séquentielle des filtres pour une sheet
    """

    def __init__(self, sheet_name: str):
        """
        Initialise le pipeline pour une sheet donnée

        Args:
            sheet_name: Nom de la sheet
        """
        self.sheet_name = sheet_name
        self.filter_configs = get_filters_for_sheet(sheet_name)
        self.filters = self._build_filters()

    def _build_filters(self) -> list[Any]:
        """
        Construit les instances de filtres à partir de la configuration

        Returns:
            Liste des instances de filtres prêts à être appliqués
        """
        filters = []

        for filter_config in self.filter_configs:
            filter_class = filter_config["filter"]
            config = filter_config.get("config", {})

            # Créer une instance du filtre
            filter_instance = filter_class(config)
            filters.append(filter_instance)

        return filters

    def apply(self, records: list[dict]) -> list[dict]:
        """
        Applique tous les filtres configurés séquentiellement

        Args:
            records: Liste des enregistrements à filtrer

        Returns:
            Liste des enregistrements après application de tous les filtres
        """
        if not self.filters:
            return records

        # Appliquer chaque filtre successivement
        processed_records = records

        for i, filter_instance in enumerate(self.filters):
            filter_name = filter_instance.__class__.__name__
            print(f"      → Filtre {i + 1}/{len(self.filters)}: {filter_name}")

            try:
                processed_records = filter_instance.apply(processed_records)
            except Exception as e:
                print(f"         ⚠️  Erreur dans {filter_name}: {e}")
                # Continuer avec les données non filtrées
                pass

        return processed_records

    def describe(self) -> str:
        """
        Retourne une description des filtres appliqués

        Returns:
            Description textuelle du pipeline
        """
        if not self.filter_configs:
            return f"Aucun filtre configuré pour {self.sheet_name}"

        lines = [f"Filtres pour {self.sheet_name}:"]

        for i, config in enumerate(self.filter_configs, 1):
            filter_class = config["filter"]
            description = config.get("description", "")
            lines.append(f"  {i}. {filter_class.__name__}")
            if description:
                lines.append(f"     {description}")

        return "\n".join(lines)


def apply_filters_if_configured(sheet_name: str, records: list[dict]) -> list[dict]:
    """
    Fonction utilitaire pour appliquer les filtres si configurés

    Args:
        sheet_name: Nom de la sheet
        records: Liste des enregistrements

    Returns:
        Liste des enregistrements filtrés
    """
    if not has_filters(sheet_name):
        return records

    pipeline = FilterPipeline(sheet_name)
    return pipeline.apply(records)