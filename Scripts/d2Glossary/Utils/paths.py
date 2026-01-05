"""
paths.py - Configuration centralisée des chemins du projet
"""
import os
from pathlib import Path

# Racine du projet (3 niveaux au-dessus de ce fichier)
PROJECT_ROOT = Path(__file__).parent.parent.parent.parent.resolve()

# Dossiers principaux
DATA_DIR = PROJECT_ROOT / "data"
SCRIPTS_DIR = PROJECT_ROOT / "Scripts" / "d2Glossary"
PROCESS_DIR = SCRIPTS_DIR / "Process"
UTILS_DIR = SCRIPTS_DIR / "Utils"

# Fichiers de données en entrée (manifest Bungie)
ITEM_DEFINITIONS = DATA_DIR / "item_definitions.json"
TRAIT_DEFINITIONS = DATA_DIR / "trait_definitions.json"
BREAKER_DEFINITIONS = DATA_DIR / "breaker_definitions.json"
DAMAGETYPE_DEFINITIONS = DATA_DIR / "damagetype_definitions.json"
MODIFIER_DEFINITIONS = DATA_DIR / "modifier_definitions.json"
SETARMOR_DEFINITIONS = DATA_DIR / "setarmor_definitions.json"
SANDBOXPERK_DEFINITIONS = DATA_DIR / "sandboxperk_definitions.json"
ARTEFACT_DEFINITIONS = DATA_DIR / "artefact_definitions.json"
ICON_DEFINITIONS = DATA_DIR / "icon_definition.json"

# Fichiers de données en sortie (enrichis)
SETARMOR_ENRICHED = DATA_DIR / "setarmor_definitions_enriched.json"
ARTEFACT_ENRICHED = DATA_DIR / "artefact_definitions_enriched.json"

# Fichier de version
VERSION_FILE = DATA_DIR / "version.json"

# Dictionnaire des manifests à télécharger
MANIFEST_LIST = {
    "DestinyInventoryItemDefinition": "item_definitions",
    "DestinyTraitDefinition": "trait_definitions",
    "DestinyBreakerTypeDefinition": "breaker_definitions",
    "DestinyDamageTypeDefinition": "damagetype_definitions",
    "DestinyActivityModifierDefinition": "modifier_definitions",
    "DestinyEquipableItemSetDefinition": "setarmor_definitions",
    "DestinySandboxPerkDefinition": "sandboxperk_definitions",
    "DestinyArtifactDefinition": "artefact_definitions",
    "DestinyIconDefinition": "icon_definition"
}

# Clés à exclure lors du nettoyage des données
KEYS_TO_EXCLUDE = [
    "uiItemDisplayStyle", "displaySource", "action", "equippingBlock",
    "translationBlock", "preview", "quality", "acquireRewardSiteHash",
    "acquireUnlockHash", "doesPostmasterPullHaveSideEffects", "nonTransferrable",
    "tooltipNotifications", "backgroundColor", "crafting",
    "stats", "investmentStats", "allowActions",
    "isWrapper", "equippable", "traitIds", "traitHashes", "index",
    "redacted", "blacklisted", "iconWatermark",
    "iconWatermarkShelved", "iconWatermarkFeatured",
    "isFeaturedItem", "isHolofoil", "isAdept",
    "flavorText", "inventory"
]

# Configuration de version.json
VERSION_CONFIG = {
    "light": [
        "data/trait_definitions.json",
        "data/breaker_definitions.json",
        "data/modifier_definitions.json",
        "data/damagetype_definitions.json",
        "data/setarmor_definitions_enriched.json",
        "data/artefact_definitions_enriched.json"
    ],
    "heavy": [
        "data/item_definitions.json",
        "data/clarity.json"
    ]
}

def ensure_data_dir():
    """Crée le dossier data s'il n'existe pas"""
    DATA_DIR.mkdir(parents=True, exist_ok=True)

def get_relative_path(file_path: Path) -> str:
    """Retourne le chemin relatif par rapport à PROJECT_ROOT"""
    try:
        return str(file_path.relative_to(PROJECT_ROOT))
    except ValueError:
        return str(file_path)