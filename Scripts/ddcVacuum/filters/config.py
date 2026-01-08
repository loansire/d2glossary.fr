"""
Configuration des filtres à appliquer pour chaque sheet
Table de correspondance sheet -> filtres
"""

from filters.name_propagation import NamePropagationFilter
from filters.name_comment_split import NameCommentSplitFilter
from filters.armor_set_description_split import ArmorSetDescriptionSplitFilter


# Configuration globale : quels filtres appliquer à quelles sheets
SHEET_FILTERS = {
    "ArmorSets": [
        {
            "filter": NamePropagationFilter,
            "config": {
                "name_field": "Name"
            },
            "description": "Propage le Name de l'item précédent si vide"
        },
        {
            "filter": NameCommentSplitFilter,
            "config": {
                "name_field": "Name",
                "comment_field": "Comment"
            },
            "description": "Sépare le Name et le Comment (qui peut contenir des \\n)"
        },
        {
            "filter": ArmorSetDescriptionSplitFilter,
            "config": {
                "name_field": "Name",
                "description_field": "Description",
                "set_name_field": "SetName",
                "piece_requirement_field": "PieceRequirement"
            },
            "description": "Extrait 'X Piece | Effect' de Description et réorganise les champs"
        }
    ],

    "WeaponPerks": [
        {
            "filter": NameCommentSplitFilter,
            "config": {
                "name_field": "Name",
                "comment_field": "Comment"
            },
            "description": "Sépare le Name et le Comment"
        }
    ],

    "OriginTraits": [
        {
            "filter": NameCommentSplitFilter,
            "config": {
                "name_field": "Name",
                "comment_field": "Comment"
            },
            "description": "Sépare le Name et le Comment"
        }
    ],

    "IntrinsicTraits": [
        {
            "filter": NameCommentSplitFilter,
            "config": {
                "name_field": "Name",
                "comment_field": "Comment"
            },
            "description": "Sépare le Name et le Comment"
        }
    ],

    # Ajouter d'autres sheets ici au besoin
    # "IntrinsicTraits": [
    #     {
    #         "filter": NameCommentSplitFilter,
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