"""
Hash Enricher Configuration
Defines mappings between ddcVacuum sheets and d2glossary data sources
"""

# Base paths
D2GLOSSARY_BASE = "../../data/en"
DDCVACUUM_BASE = "data/simple"

# Mapping configuration
# Structure: {
#     "ddcVacuum_sheet_name": {
#         "source": "d2glossary JSON file name",
#         "name_path": "path.to.name.field",
#         "hash_path": "path.to.hash.field",
#         "array_path": "optional.path.to.array" (si le hash est dans un array)
#     }
# }

HASH_MAPPINGS = {
    "ArmorSets": {
        "source": "setarmor_definitions_enriched.json",
        "name_path": "setPerks.displayProperties.name",
        "hash_path": "setPerks.sandboxPerkHash",
        "array_path": "setPerks"  # Les données sont dans un array setPerks
    },

    "ArmorSets": {
        "source": "setarmor_definitions_enriched.json",
        "name_path": "setPerks.displayProperties.name",
        "hash_path": "setPerks.sandboxPerkHash",
        "array_path": "setPerks"  # Les données sont dans un array setPerks
    }
    # Ajouter d'autres mappings ici au fur et à mesure
}


def get_nested_value(data: dict, path: str):
    """
    Récupère une valeur dans un dictionnaire imbriqué via un chemin en notation pointée.

    Args:
        data: Dictionnaire source
        path: Chemin vers la valeur (ex: "displayProperties.name")

    Returns:
        La valeur trouvée ou None

    Example:
        >>> data = {"a": {"b": {"c": "value"}}}
        >>> get_nested_value(data, "a.b.c")
        "value"
    """
    keys = path.split('.')
    current = data

    for key in keys:
        if isinstance(current, dict) and key in current:
            current = current[key]
        else:
            return None

    return current


def set_nested_value(data: dict, path: str, value):
    """
    Définit une valeur dans un dictionnaire imbriqué via un chemin en notation pointée.

    Args:
        data: Dictionnaire cible
        path: Chemin vers la valeur (ex: "displayProperties.name")
        value: Valeur à définir

    Example:
        >>> data = {}
        >>> set_nested_value(data, "a.b.c", "value")
        >>> data
        {"a": {"b": {"c": "value"}}}
    """
    keys = path.split('.')
    current = data

    for i, key in enumerate(keys[:-1]):
        if key not in current:
            current[key] = {}
        current = current[key]

    current[keys[-1]] = value