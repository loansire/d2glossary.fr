"""
paths.py - Configuration centralisée des chemins du projet (version multilingue)
Utilise une approche WHITELIST : on ne garde que les clés explicitement listées
"""
import os
from pathlib import Path

# Racine du projet
PROJECT_ROOT = Path(__file__).parent.parent.parent.parent.resolve()

# Dossiers principaux
DATA_DIR = PROJECT_ROOT / "data"
SCRIPTS_DIR = PROJECT_ROOT / "Scripts" / "d2Glossary"
PROCESS_DIR = SCRIPTS_DIR / "Process"
UTILS_DIR = SCRIPTS_DIR / "Utils"

# Langues supportées
SUPPORTED_LANGUAGES = ["fr", "en"]
DEFAULT_LANGUAGE = "fr"

# Fonction pour obtenir les chemins localisés
def get_localized_path(filename: str, lang: str = DEFAULT_LANGUAGE) -> Path:
    """Retourne le chemin d'un fichier pour une langue donnée"""
    if lang not in SUPPORTED_LANGUAGES:
        raise ValueError(f"Langue non supportée: {lang}. Langues disponibles: {SUPPORTED_LANGUAGES}")
    return DATA_DIR / lang / filename

# Fonction pour obtenir tous les chemins localisés
def get_all_localized_paths(filename: str) -> dict[str, Path]:
    """Retourne un dict {lang: path} pour toutes les langues"""
    return {lang: get_localized_path(filename, lang) for lang in SUPPORTED_LANGUAGES}

# Noms de fichiers (sans langue)
ITEM_DEFINITIONS_FILE = "item_definitions.json"
TRAIT_DEFINITIONS_FILE = "trait_definitions.json"
BREAKER_DEFINITIONS_FILE = "breaker_definitions.json"
DAMAGETYPE_DEFINITIONS_FILE = "damagetype_definitions.json"
MODIFIER_DEFINITIONS_FILE = "modifier_definitions.json"
SETARMOR_DEFINITIONS_FILE = "setarmor_definitions.json"
SANDBOXPERK_DEFINITIONS_FILE = "sandboxperk_definitions.json"
ARTEFACT_DEFINITIONS_FILE = "artefact_definitions.json"
ICON_DEFINITIONS_FILE = "icon_definition.json"
SETARMOR_ENRICHED_FILE = "setarmor_definitions_enriched.json"
ARTEFACT_ENRICHED_FILE = "artefact_definitions_enriched.json"
DDCVACUUM_FILE = "ddcvacuum.json"

# Chemins par défaut (français) pour compatibilité
ITEM_DEFINITIONS = get_localized_path(ITEM_DEFINITIONS_FILE)
TRAIT_DEFINITIONS = get_localized_path(TRAIT_DEFINITIONS_FILE)
BREAKER_DEFINITIONS = get_localized_path(BREAKER_DEFINITIONS_FILE)
DAMAGETYPE_DEFINITIONS = get_localized_path(DAMAGETYPE_DEFINITIONS_FILE)
MODIFIER_DEFINITIONS = get_localized_path(MODIFIER_DEFINITIONS_FILE)
SETARMOR_DEFINITIONS = get_localized_path(SETARMOR_DEFINITIONS_FILE)
SANDBOXPERK_DEFINITIONS = get_localized_path(SANDBOXPERK_DEFINITIONS_FILE)
ARTEFACT_DEFINITIONS = get_localized_path(ARTEFACT_DEFINITIONS_FILE)
ICON_DEFINITIONS = get_localized_path(ICON_DEFINITIONS_FILE)
SETARMOR_ENRICHED = get_localized_path(SETARMOR_ENRICHED_FILE)
ARTEFACT_ENRICHED = get_localized_path(ARTEFACT_ENRICHED_FILE)

# Fichier de version (commun à toutes les langues)
VERSION_FILE = DATA_DIR / "version.json"

# Dictionnaire des manifests à télécharger
MANIFEST_LIST = {
    "DestinyInventoryItemDefinition": ITEM_DEFINITIONS_FILE,
    "DestinyTraitDefinition": TRAIT_DEFINITIONS_FILE,
    "DestinyBreakerTypeDefinition": BREAKER_DEFINITIONS_FILE,
    "DestinyDamageTypeDefinition": DAMAGETYPE_DEFINITIONS_FILE,
    "DestinyActivityModifierDefinition": MODIFIER_DEFINITIONS_FILE,
    "DestinyEquipableItemSetDefinition": SETARMOR_DEFINITIONS_FILE,
    "DestinySandboxPerkDefinition": SANDBOXPERK_DEFINITIONS_FILE,
    "DestinyArtifactDefinition": ARTEFACT_DEFINITIONS_FILE,
    "DestinyIconDefinition": ICON_DEFINITIONS_FILE
}

# =============================================================================
# WHITELIST PAR TYPE DE DÉFINITION
# On ne garde QUE les clés listées ici (approche whitelist)
# Utilise la notation pointée pour les clés imbriquées
# =============================================================================

# Clés communes à la plupart des définitions
COMMON_WHITELIST = [
    "hash",
    "displayProperties",          # Objet complet (name, description, icon, hasIcon)
]

# Configuration whitelist par type de manifest
MANIFEST_WHITELIST = {
    # Items (perks, mods, etc.) - le plus gros fichier
    "item_definitions": [
        *COMMON_WHITELIST,
        "itemType",
        "itemSubType",
        "classType",
        "breakerType",
        "itemCategoryHashes",
        "traitIds",
        "perks",                    # Pour l'enrichissement artefact (array complet)
    ],

    # Traits élémentaires
    "trait_definitions": [
        *COMMON_WHITELIST,
    ],

    # Types de champions (breaker)
    "breaker_definitions": [
        *COMMON_WHITELIST,
    ],

    # Types de dégâts
    "damagetype_definitions": [
        *COMMON_WHITELIST,
        "transparentIconPath",
    ],

    # Modificateurs d'activités
    "modifier_definitions": [
        *COMMON_WHITELIST,
    ],

    # Sets d'armure (DestinyEquipableItemSetDefinition)
    # Structure Bungie: setItems (array de hashes), setPerks (à enrichir)
    "setarmor_definitions": [
        *COMMON_WHITELIST,
        "setType",
        "setIsFeatured",
        "setItems",                 # Array de itemHash (pièces d'armure)
        "setPerks",                 # Array avec sandboxPerkHash et requiredSetCount
    ],

    # Perks sandbox (pour enrichissement des sets et artefacts)
    "sandboxperk_definitions": [
        *COMMON_WHITELIST,
        "perkIdentifier",
        "isDisplayable",
        "damageType",
        "damageTypeHash",
    ],

    # Artefacts saisonniers
    "artefact_definitions": [
        *COMMON_WHITELIST,
        "tiers",                    # Array complet des tiers avec items
    ],

    # Icônes
    "icon_definition": [
        *COMMON_WHITELIST,
    ],
}

def get_whitelist_for_definition(definition_type: str) -> list[str]:
    """
    Retourne la whitelist pour un type de définition donné

    Args:
        definition_type: Type de définition (ex: "item_definitions")

    Returns:
        Liste des clés à conserver
    """
    # Retirer l'extension .json si présente
    clean_type = definition_type.replace(".json", "")
    return MANIFEST_WHITELIST.get(clean_type, COMMON_WHITELIST)

def is_key_whitelisted(key_path: str, whitelist: list[str]) -> bool:
    """
    Vérifie si une clé (ou son chemin parent) est dans la whitelist

    Args:
        key_path: Chemin de la clé (ex: "displayProperties.name")
        whitelist: Liste des clés autorisées

    Returns:
        True si la clé est autorisée
    """
    # Vérification directe
    if key_path in whitelist:
        return True

    # Vérifier si un parent est dans la whitelist (pour les objets complets)
    parts = key_path.split('.')
    for i in range(len(parts)):
        parent_path = '.'.join(parts[:i+1])
        if parent_path in whitelist:
            return True

    # Vérifier si c'est un enfant d'une clé whitelistée
    for whitelisted_key in whitelist:
        if key_path.startswith(whitelisted_key + '.'):
            return True

    return False


# Configuration de version.json
def get_version_config(lang: str = None) -> dict:
    """
    Retourne la configuration des fichiers pour version.json
    Si lang=None, retourne la config pour toutes les langues
    """
    if lang is None:
        # Configuration multi-langue
        config = {"languages": {}}
        for language in SUPPORTED_LANGUAGES:
            config["languages"][language] = {
                "light": [
                    f"data/{language}/{TRAIT_DEFINITIONS_FILE}",
                    f"data/{language}/{BREAKER_DEFINITIONS_FILE}",
                    f"data/{language}/{MODIFIER_DEFINITIONS_FILE}",
                    f"data/{language}/{DAMAGETYPE_DEFINITIONS_FILE}",
                    f"data/{language}/{SETARMOR_ENRICHED_FILE}",
                    f"data/{language}/{ARTEFACT_ENRICHED_FILE}"
                ],
                "heavy": [
                    f"data/{language}/{ITEM_DEFINITIONS_FILE}",
                    f"data/{DDCVACUUM_FILE}"
                ]
            }
        return config
    else:
        # Configuration pour une langue spécifique
        return {
            "light": [
                f"data/{lang}/{TRAIT_DEFINITIONS_FILE}",
                f"data/{lang}/{BREAKER_DEFINITIONS_FILE}",
                f"data/{lang}/{MODIFIER_DEFINITIONS_FILE}",
                f"data/{lang}/{DAMAGETYPE_DEFINITIONS_FILE}",
                f"data/{lang}/{SETARMOR_ENRICHED_FILE}",
                f"data/{lang}/{ARTEFACT_ENRICHED_FILE}"
            ],
            "heavy": [
                f"data/{lang}/{ITEM_DEFINITIONS_FILE}",
                f"data/{DDCVACUUM_FILE}"
            ]
        }

def ensure_data_dirs():
    """Crée les dossiers data pour toutes les langues"""
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    for lang in SUPPORTED_LANGUAGES:
        (DATA_DIR / lang).mkdir(parents=True, exist_ok=True)

def get_relative_path(file_path: Path) -> str:
    """Retourne le chemin relatif par rapport à PROJECT_ROOT"""
    try:
        return str(file_path.relative_to(PROJECT_ROOT))
    except ValueError:
        return str(file_path)