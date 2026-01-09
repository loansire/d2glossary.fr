"""
Hash Matcher - Finds hash matches between ddcVacuum and d2glossary data
"""

import json
from typing import List, Dict, Any, Optional
from .config import get_nested_value


def find_hash_matches(
        vacuum_name: str,
        glossary_data: Dict[str, Any],
        name_path: str,
        hash_path: str,
        array_path: Optional[str] = None
) -> List[Dict[str, Any]]:
    """
    Recherche tous les hash correspondant à un nom dans les données d2glossary.
    La comparaison des noms est insensible à la casse.

    Args:
        vacuum_name: Le nom à rechercher (ex: "Force Converter")
        glossary_data: Les données d2glossary complètes
        name_path: Chemin vers le champ name (ex: "setPerks.displayProperties.name")
        hash_path: Chemin vers le champ hash (ex: "setPerks.sandboxPerkHash")
        array_path: Chemin optionnel vers un array (ex: "setPerks")

    Returns:
        Liste de dictionnaires contenant les matches trouvés:
        [
            {
                "name": "Force Converter",
                "hash": 2140508055,
                "parent_hash": 1223381128,  # Hash du parent (ex: hash du set)
                "parent_name": "AION Renewal"
            }
        ]

    Example:
        >>> matches = find_hash_matches(
        ...     "Force Converter",
        ...     glossary_data,
        ...     "setPerks.displayProperties.name",
        ...     "setPerks.sandboxPerkHash",
        ...     "setPerks"
        ... )
    """
    matches = []

    # Parcourir tous les items du glossary
    for parent_hash, item in glossary_data.items():
        # Si array_path est spécifié, on doit chercher dans un array
        if array_path:
            array = get_nested_value(item, array_path)

            if not array or not isinstance(array, list):
                continue

            # Parcourir chaque élément de l'array
            for element in array:
                # Extraire le nom depuis l'élément de l'array
                # On retire le préfixe array_path du name_path
                element_name_path = name_path.replace(f"{array_path}.", "")
                element_name = get_nested_value(element, element_name_path)

                # Vérifier si le nom correspond (insensible à la casse)
                if element_name and element_name.strip().lower() == vacuum_name.strip().lower():
                    # Extraire le hash depuis l'élément de l'array
                    element_hash_path = hash_path.replace(f"{array_path}.", "")
                    element_hash = get_nested_value(element, element_hash_path)

                    if element_hash:
                        # Récupérer le nom du parent
                        parent_name = get_nested_value(item, "displayProperties.name")

                        matches.append({
                            "name": element_name,
                            "hash": element_hash,
                            "parent_hash": parent_hash,
                            "parent_name": parent_name
                        })
        else:
            # Cas simple : recherche directe dans l'item
            item_name = get_nested_value(item, name_path)

            # Vérifier si le nom correspond (insensible à la casse)
            if item_name and item_name.strip().lower() == vacuum_name.strip().lower():
                item_hash = get_nested_value(item, hash_path)

                if item_hash:
                    matches.append({
                        "name": item_name,
                        "hash": item_hash,
                        "parent_hash": parent_hash,
                        "parent_name": None
                    })

    return matches


def enrich_record_with_hashes(
        record: Dict[str, Any],
        matches: List[Dict[str, Any]]
) -> List[Dict[str, Any]]:
    """
    Enrichit un record ddcVacuum avec les hash trouvés.
    Si plusieurs hash sont trouvés, crée plusieurs instances du record.

    Args:
        record: Record ddcVacuum original
        matches: Liste des matches trouvés par find_hash_matches

    Returns:
        Liste de records enrichis (un par match)

    Example:
        >>> record = {"Name": "Force Converter", "Description": "..."}
        >>> matches = [{"hash": 2140508055, "parent_hash": 1223381128, ...}]
        >>> enriched = enrich_record_with_hashes(record, matches)
        >>> enriched[0]["hash"]
        2140508055
    """
    if not matches:
        # Aucun match trouvé : retourner le record original avec hash = None
        enriched_record = record.copy()
        enriched_record["hash"] = None
        enriched_record["hash_warning"] = "No matching hash found in d2glossary"
        return [enriched_record]

    # Créer une instance par match
    enriched_records = []
    for match in matches:
        enriched_record = record.copy()
        enriched_record["hash"] = match["hash"]
        enriched_record["parentHash"] = match["parent_hash"]

        if match["parent_name"]:
            enriched_record["parentName"] = match["parent_name"]

        # Ajouter un warning si plusieurs matches
        if len(matches) > 1:
            enriched_record["hash_warning"] = f"Multiple matches found ({len(matches)} total)"

        enriched_records.append(enriched_record)

    return enriched_records