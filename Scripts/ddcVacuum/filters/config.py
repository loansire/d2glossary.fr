"""
Configuration des filtres à appliquer pour chaque sheet
Table de correspondance sheet -> filtres
"""

from filters.name_propagation import NamePropagationFilter
from filters.name_source_split import NameSourceSplitFilter

# Configuration globale : quels filtres appliquer à quelles sheets
SHEET_FILTERS = {
    "ArmorSets": [
        {
            "filter": NameSourceSplitFilter,
            "config": {
                "name_field": "Name",
                "source_field": "source"
            },
            "description": "Sépare le Name et le source quand il y a des \\n"
        },
        {
            "filter": NamePropagationFilter,
            "config": {
                "name_field": "Name"
            },
            "description": "Propage le Name de l'item précédent si vide"
        }
    ],

    "WeaponPerks": [
        {
            "filter": NameSourceSplitFilter,
            "config": {
                "name_field": "Name",
                "source_field": "source"
            },
            "description": "Sépare le Name et le source"
        }
    ],

    # Ajouter d'autres sheets ici au besoin
    # "IntrinsicTraits": [
    #     {
    #         "filter": NameSourceSplitFilter,
    #         "config": {...}
    #     }
    # ],
}


def get_filters_for_sheet(sheet_name: str) -> list[dict]:
    """
    Retourne la liste des filtres configurés pour une sheet donnée

    Args:
        sheet_name: Nom de la sheet

    Returns:
        Liste des configurations de filtres
    """
    return SHEET_FILTERS.get(sheet_name, [])


def has_filters(sheet_name: str) -> bool:
    """
    Vérifie si une sheet a des filtres configurés

    Args:
        sheet_name: Nom de la sheet

    Returns:
        True si des filtres sont configurés
    """
    return sheet_name in SHEET_FILTERS and len(SHEET_FILTERS[sheet_name]) > 0