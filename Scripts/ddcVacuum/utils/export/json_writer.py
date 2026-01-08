"""
JSON export utilities

Handles JSON file writing with NaN/None value sanitization
"""

import json


def clean_nan_values(obj):
    """
    Nettoie récursivement les valeurs NaN, None, et chaînes vides

    Args:
        obj: Objet à nettoyer (dict, list, ou valeur simple)

    Returns:
        Objet nettoyé sans NaN/None/chaînes vides

    Example:
        >>> data = {"a": 1, "b": None, "c": "", "d": "NaN"}
        >>> clean_nan_values(data)
        {"a": 1}
    """
    if isinstance(obj, dict):
        return {
            k: clean_nan_values(v)
            for k, v in obj.items()
            if v is not None
               and v != ""
               and str(v).lower() != "nan"
        }
    elif isinstance(obj, list):
        return [
            clean_nan_values(item)
            for item in obj
            if item is not None
               and item != ""
               and str(item).lower() != "nan"
        ]
    else:
        # Si c'est NaN (float) ou la chaîne "NaN", retourner None
        if str(obj).lower() == "nan":
            return None
        return obj


def save_json(data: any, filepath: str) -> None:
    """
    Sauvegarde des données en JSON en nettoyant les NaN

    Args:
        data: Données à sauvegarder
        filepath: Chemin du fichier de sortie

    Example:
        >>> save_json({"key": "value"}, "output.json")
    """
    # Nettoyer les données
    cleaned_data = clean_nan_values(data)

    # Écrire le fichier JSON
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(cleaned_data, f, ensure_ascii=False, indent=2)