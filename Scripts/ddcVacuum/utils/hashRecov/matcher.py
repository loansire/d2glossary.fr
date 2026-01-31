"""
Hash Matcher - Finds hash matches between ddcVacuum and d2glossary data
Avec normalisation Unicode pour gérer les accents/diacritiques
"""

import json
import unicodedata
from typing import List, Dict, Any, Optional
from .config import get_nested_value


def normalize_name(name: str) -> str:
    """
    Normalise un nom pour la comparaison :
    - Retire les accents/diacritiques (ä → a, é → e, etc.)
    - Convertit en minuscules
    - Supprime les espaces en début/fin

    Args:
        name: Nom à normaliser

    Returns:
        Nom normalisé

    Examples:
        >>> normalize_name("Häkke Breach Armaments")
        "hakke breach armaments"
        >>> normalize_name("Éclat Solaire")
        "eclat solaire"
    """
    if not name:
        return ""

    # Normaliser en forme NFD (décompose les caractères accentués)
    # Ex: "ä" devient "a" + combining diaeresis
    normalized = unicodedata.normalize('NFD', name)

    # Retirer les marques diacritiques (catégorie 'Mn' = Mark, Nonspacing)
    without_diacritics = ''.join(
        char for char in normalized
        if unicodedata.category(char) != 'Mn'
    )

    # Minuscules et strip
    return without_diacritics.lower().strip()


def names_match(name1: str, name2: str) -> bool:
    """
    Compare deux noms de manière insensible aux accents et à la casse

    Args:
        name1: Premier nom
        name2: Deuxième nom

    Returns:
        True si les noms correspondent
    """
    return normalize_name(name1) == normalize_name(name2)


def find_hash_matches(
        vacuum_name: str,
        glossary_data: Dict[str, Any],
        name_path: str,
        hash_path: str,
        array_path: Optional[str] = None
) -> List[Dict[str, Any]]:
    """
    Recherche tous les hash correspondant à un nom dans les données d2glossary.
    La comparaison des noms est insensible à la casse ET aux accents/diacritiques.

    Supporte les structures imbriquées avec array_path utilisant la notation:
    - "setPerks" : array simple
    - "tiers.items" : array imbriqué (parcourt tiers[], puis items[] dans chaque tier)

    Args:
        vacuum_name: Le nom à rechercher (ex: "Force Converter", "Hakke Breach Armaments")
        glossary_data: Les données d2glossary complètes
        name_path: Chemin vers le champ name (ex: "tiers.items.name")
        hash_path: Chemin vers le champ hash (ex: "tiers.items.perkHash")
        array_path: Chemin optionnel vers un array (ex: "tiers.items")

    Returns:
        Liste de dictionnaires contenant les matches trouvés
    """
    matches = []
    normalized_vacuum_name = normalize_name(vacuum_name)

    # Parcourir tous les items du glossary
    for parent_hash, item in glossary_data.items():
        if array_path:
            # Collecter tous les éléments à vérifier (gère les arrays imbriqués)
            elements = _collect_nested_elements(item, array_path)

            for element, element_context in elements:
                # Calculer le chemin relatif pour name et hash
                element_name_path = _get_relative_path(name_path, array_path)
                element_hash_path = _get_relative_path(hash_path, array_path)

                element_name = get_nested_value(element, element_name_path)

                # Vérifier si le nom correspond (insensible à la casse ET aux accents)
                if element_name and element_name.strip() and normalize_name(element_name) == normalized_vacuum_name:
                    element_hash = get_nested_value(element, element_hash_path)

                    # Ignorer si pas de hash ou hash null
                    if element_hash:
                        parent_name = get_nested_value(item, "displayProperties.name")

                        match_info = {
                            "name": element_name,
                            "hash": element_hash,
                            "parent_hash": parent_hash,
                            "parent_name": parent_name
                        }

                        # Ajouter le contexte (ex: tier info pour artifacts)
                        if element_context:
                            match_info["context"] = element_context

                        matches.append(match_info)
        else:
            # Cas simple : recherche directe dans l'item
            item_name = get_nested_value(item, name_path)

            if item_name and item_name.strip() and normalize_name(item_name) == normalized_vacuum_name:
                item_hash = get_nested_value(item, hash_path)

                if item_hash:
                    matches.append({
                        "name": item_name,
                        "hash": item_hash,
                        "parent_hash": parent_hash,
                        "parent_name": None
                    })

    return matches


def _collect_nested_elements(data: Dict[str, Any], array_path: str) -> List[tuple]:
    """
    Collecte tous les éléments d'un chemin d'arrays imbriqués.

    Args:
        data: Dictionnaire source
        array_path: Chemin avec notation pointée (ex: "tiers.items")

    Returns:
        Liste de tuples (element, context) où context contient des infos sur le parent

    Example:
        Pour array_path="tiers.items":
        - Parcourt data["tiers"] (array)
        - Pour chaque tier, parcourt tier["items"] (array)
        - Retourne tous les items avec leur contexte (tier info)
    """
    path_parts = array_path.split('.')

    def recurse(current_data, remaining_path, context=None):
        """Récursivement collecter les éléments"""
        if context is None:
            context = {}

        if not remaining_path:
            # Fin du chemin, retourner l'élément actuel
            return [(current_data, context)]

        current_key = remaining_path[0]
        rest_path = remaining_path[1:]

        current_array = current_data.get(current_key) if isinstance(current_data, dict) else None

        if not current_array or not isinstance(current_array, list):
            return []

        results = []
        for i, element in enumerate(current_array):
            # Créer un contexte enrichi pour cet élément
            new_context = context.copy()

            # Ajouter des infos de contexte utiles
            if current_key == "tiers" and isinstance(element, dict):
                new_context["tierIndex"] = i
                new_context["tierTitle"] = element.get("displayTitle", f"Tier {i+1}")

            # Continuer la récursion
            results.extend(recurse(element, rest_path, new_context))

        return results

    return recurse(data, path_parts)


def _get_relative_path(full_path: str, array_path: str) -> str:
    """
    Calcule le chemin relatif après le array_path.

    Args:
        full_path: Chemin complet (ex: "tiers.items.name")
        array_path: Chemin de l'array (ex: "tiers.items")

    Returns:
        Chemin relatif (ex: "name")
    """
    if not array_path:
        return full_path

    # Retirer le préfixe array_path du full_path
    if full_path.startswith(array_path + "."):
        return full_path[len(array_path) + 1:]

    # Si le chemin ne commence pas par array_path, retourner tel quel
    return full_path


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

        if match.get("parent_name"):
            enriched_record["parentName"] = match["parent_name"]

        # Ajouter le contexte si présent (ex: tier info)
        if match.get("context"):
            for key, value in match["context"].items():
                enriched_record[key] = value

        # Ajouter un warning si plusieurs matches
        if len(matches) > 1:
            enriched_record["hash_warning"] = f"Multiple matches found ({len(matches)} total)"

        enriched_records.append(enriched_record)

    return enriched_records