"""
enrichArmorSet.py - Enrichissement des données d'armures et artefacts (multilingue)
"""
import json
from pathlib import Path
import sys
import re

# Ajouter le dossier parent au path pour les imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from Utils.paths import (
    SUPPORTED_LANGUAGES, DEFAULT_LANGUAGE, get_localized_path, get_relative_path,
    SETARMOR_DEFINITIONS_FILE, SANDBOXPERK_DEFINITIONS_FILE,
    ITEM_DEFINITIONS_FILE, ARTEFACT_DEFINITIONS_FILE,
    SETARMOR_ENRICHED_FILE, ARTEFACT_ENRICHED_FILE,
    COLLECTIBLE_DEFINITIONS_FILE
)


# =============================================================================
# NETTOYAGE DES SOURCES (sourceString)
# =============================================================================

# Mentions techniques à ignorer (pas de vraie source de drop).
IGNORED_SOURCES = [
    "attributs aleatoires : cet objet ne peut pas etre acquis de nouveau dans les collections",
    "random perks: this item cannot be reacquired from collections",
]

# Mapping manuel des sources spéciales.
# Clé = sourceString après normalisation : préfixe "Source :" retiré, point final retiré,
#       espaces insécables convertis en espaces simples, espaces multiples réduits.
# Valeur = résultat final affiché, retourné tel quel.
SOURCE_MANUAL_MAP = {
    # === EN ===
    'Dungeon "Duality"': "« Duality » Dungeon",
    "Vesper's Host": "« Vesper's Host » Dungeon",
    "Sundered Doctrine": "« Sundered Doctrine » Dungeon",
    "Equilibrium": "« Equilibrium » Dungeon",
    "Last Wish raid": "« Last Wish » Raid",

    # === FR ===
    "Hôte Vesper": "Donjon « Hôte Vesper »",
    "Dogme fragmenté": "Donjon « Dogme fragmenté »",
    "Équilibre": "Donjon « Équilibre »",
    "Raid Orée du Salut": "Raid « Orée du Salut »",
}

# Override manuel de source PAR SET (clé = set_id du JSON enrichi).
# Prioritaire sur la détection automatique : remplit les `source: null`
# ET écrase une source existante si besoin.
# Valeur : soit une string (commune à toutes les langues),
#          soit un dict {"fr": ..., "en": ...} (fallback sur DEFAULT_LANGUAGE).
# Une valeur vide ("") ou absente est ignorée → comportement automatique conservé.
SOURCE_SET_OVERRIDE = {
    "239346083":  {"fr": "Vendeur Zavala", "en": "Zavala Vendor"},
    "1083114430": {"fr": "Vendeur Zavala", "en": "Zavala Vendor"},
    "2751989785": {"fr": "Vendeur Zavala", "en": "Zavala Vendor"},
    "3734029045": {"fr": "Vendeur Zavala", "en": "Zavala Vendor"},
    "2391762223": {"fr": "Vendeur Zavala", "en": "Zavala Vendor"},
    "499993704":  {"fr": "Vendeur Zavala // Opération Solo/Escouade", "en": "Zavala Vendor // Solo/FireTeam ops"},
    "2461275960": {"fr": "Vendeur Zavala // Opération en Arène/Prestige", "en": "Zavala Vendor // Arena/Pinnacle ops"},
    "3252452908": {"fr": "Vendeur Shaxx", "en": "Vendor Shaxx"},
    "2947197258": {"fr": "Vendeur Shaxx", "en": "Vendor Shaxx"},
    "2258577662": {"fr": "Vendeur Shaxx", "en": "Vendor Shaxx"},
    "50540439":   {"fr": "Vendeurs Shaxx/Zavala", "en": "Shaxx/Zavala Vendors"},
    "2554324129": {"fr": "Exploration de la ZME", "en": "Exploring EDZ"},
    "2250480800": {"fr": "Exploration de la Lune", "en": "Exploring Moon"},
    "3120219904": {"fr": "Exploration de Nessos", "en": "Exploring Nessus"},
    "3090557911": {"fr": "Exploration de Europe", "en": "Exploring Europa"},
    "3283637820": {"fr": "Exploration de Neomuna", "en": "Exploring Neomuna"},
    "1625535837": {"fr": "Exploration du Coeur Pâle", "en": "Exploring Pale heart"},
    "222121557":  {"fr": "Exploration du Cosmodrome", "en": "Exploring Cosmodrome"},
    "428813981":  {"fr": "Exploration de la Cité des Rêves", "en": "Exploring Dreaming city"},
    "2481896422": {"fr": "Exploration du Monde Trône de Savathûn", "en": "Exploring Court of Savathûn"},
}


def _resolve_set_override(set_id, lang):
    """
    Retourne la source override pour un set/langue, ou None si absente/vide.

    - String : valeur commune à toutes les langues.
    - Dict : on prend la langue demandée, puis fallback DEFAULT_LANGUAGE.
    - Vide ("" ou None) : ignoré (None retourné) → détection auto conservée.
    """
    override = SOURCE_SET_OVERRIDE.get(str(set_id))
    if override is None:
        return None

    if isinstance(override, dict):
        value = override.get(lang) or override.get(DEFAULT_LANGUAGE)
    else:
        value = override  # string commune

    value = (value or "").strip()
    return value or None


def _normalize_for_compare(text):
    """Minuscule + suppression accents + normalisation espaces (insécables inclus)."""
    import unicodedata
    text = text.lower()
    text = text.replace('\u00a0', ' ').replace('\u202f', ' ')
    text = unicodedata.normalize('NFD', text)
    text = ''.join(c for c in text if unicodedata.category(c) != 'Mn')
    text = re.sub(r'\s+', ' ', text).strip()
    return text


def _replace_quotes(text):
    """Remplace les guillemets droits " par paires : 1er → « , 2e → » , etc."""
    result = []
    opening = True
    for ch in text:
        if ch == '"':
            result.append('«\u00a0' if opening else '\u00a0»')
            opening = not opening
        else:
            result.append(ch)
    return ''.join(result)


def _clean_source(source):
    """
    Nettoie un sourceString :
    - normalise les espaces insécables
    - retire le préfixe "Source :" (FR/EN)
    - remplace les guillemets droits par « » (par paires)
    - retire le préfixe "Complete/Terminer" + conjugaisons
    - retire TOUS les points
    - met la 1re lettre en majuscule
    """
    # 0. Normaliser les espaces insécables
    source = source.replace('\u00a0', ' ').replace('\u202f', ' ')

    # 1. Retirer le préfixe "Source :" / "Source:" / "Source"
    source = re.sub(r'^\s*source\s*:?\s*', '', source, flags=re.IGNORECASE).strip()

    # 2. Remplacer les guillemets droits par « » (par paires)
    source = _replace_quotes(source)

    # 3. Retirer le préfixe d'action (FR/EN : complete/terminer + conjugaisons)
    source = re.sub(
        r'^\s*(completez|complete|terminez|terminer|termine|terminé|terminée)\s+(the|le|la|les|des|du)?\s*',
        '',
        source,
        flags=re.IGNORECASE
    ).strip()

    # 4. Retirer TOUS les points
    source = source.replace('.', '')

    # 5. Réduire les espaces multiples (hors insécables introduits par _replace_quotes)
    source = re.sub(r'[ \t]{2,}', ' ', source).strip()

    # 6. Majuscule sur le 1er caractère
    if source:
        source = source[0].upper() + source[1:]

    return source.strip()


def get_item_source(item_def, collectible_data):
    """
    Récupère la source de drop d'un item via sa fiche collection.
    item.collectibleHash → DestinyCollectibleDefinition[hash].sourceString
    Priorité : mapping manuel > mentions ignorées > nettoyage standard.
    Retourne None si pas de source exploitable.
    """
    coll_hash = item_def.get("collectibleHash")
    if not coll_hash:
        return None
    coll = collectible_data.get(str(coll_hash))
    if not coll:
        return None
    raw = coll.get("sourceString", "").strip()
    if not raw:
        return None

    # Base de comparaison : insécables → espaces simples, préfixe "Source :" + point final retirés
    base = raw.replace('\u00a0', ' ').replace('\u202f', ' ')
    base = re.sub(r'^\s*source\s*:?\s*', '', base, flags=re.IGNORECASE)
    base = re.sub(r'\s+', ' ', base).strip().rstrip(' .').strip()

    # 1. Mapping manuel prioritaire (valeur retournée telle quelle)
    if base in SOURCE_MANUAL_MAP:
        return SOURCE_MANUAL_MAP[base]

    # 2. Ignorer les mentions techniques
    if _normalize_for_compare(base) in IGNORED_SOURCES:
        return None

    # 3. Nettoyage standard
    cleaned = _clean_source(raw)
    return cleaned or None


# =============================================================================
# I/O JSON
# =============================================================================

def load_json(file_path):
    """Charge un fichier JSON"""
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        print(f"❌ Fichier non trouvé: {get_relative_path(file_path)}")
        return None
    except json.JSONDecodeError as e:
        print(f"❌ Erreur de parsing JSON: {get_relative_path(file_path)}: {e}")
        return None


def save_json(data, file_path):
    """Sauvegarde des données en JSON"""
    try:
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False)
        return True
    except Exception as e:
        print(f"❌ Erreur d'écriture: {get_relative_path(file_path)}: {e}")
        return False


# =============================================================================
# ENRICHISSEMENT
# =============================================================================

def enrich_setarmor(setarmor_data, sandboxperk_data, item_data, collectible_data, lang):
    """Enrichit les données des sets d'armure"""
    for set_id, set_info in setarmor_data.items():

        # Enrichir les setPerks avec sandboxperk_definitions
        if "setPerks" in set_info:
            for perk in set_info["setPerks"]:
                perk_hash = str(perk["sandboxPerkHash"])
                if perk_hash in sandboxperk_data:
                    perk_def = sandboxperk_data[perk_hash].get("displayProperties", {})
                    perk["displayProperties"] = {
                        "name": perk_def.get("name", ""),
                        "description": perk_def.get("description", ""),
                        "icon": perk_def.get("icon", None),
                    }

        # Enrichir les setItems directement + récupérer la source
        if "setItems" in set_info:
            enriched_items = []
            set_source = None                       # source au niveau du set
            for item_hash in set_info["setItems"]:
                item_hash_str = str(item_hash)
                if item_hash_str in item_data:
                    item_def = item_data[item_hash_str]
                    display = item_def.get("displayProperties", {})
                    item_source = get_item_source(item_def, collectible_data)

                    # Mémoriser la 1re source trouvée comme source du set
                    if item_source and not set_source:
                        set_source = item_source

                    enriched_items.append({
                        "hash": item_hash,
                        "name": display.get("name", ""),
                        "icon": display.get("icon", None),
                        "source": item_source,        # source par item (fallback futur)
                    })
            set_info["setItems"] = enriched_items
            set_info["source"] = set_source           # source du set (peut être None)

        # Override manuel par set (prioritaire) : écrase l'auto / remplit le null.
        # Une valeur vide dans SOURCE_SET_OVERRIDE est ignorée (retourne None).
        override = _resolve_set_override(set_id, lang)
        if override is not None:
            set_info["source"] = override

    return setarmor_data


def enrich_artefact(artefact_data, sandboxperk_data, item_data):
    """Enrichit les données des artefacts"""
    for artefact_id, artefact_info in artefact_data.items():

        if "tiers" not in artefact_info:
            continue

        for tier in artefact_info["tiers"]:
            if "items" not in tier:
                continue

            enriched_items = []
            for item in tier["items"]:
                item_hash = item["itemHash"]
                item_hash_str = str(item_hash)

                enriched_item = {
                    "itemHash": item_hash,
                    "perkHash": None,
                    "name": "",
                    "description": "",
                    "icon": None,
                }

                # Chercher l'item dans DestinyInventoryItemDefinition
                if item_hash_str in item_data:
                    item_def = item_data[item_hash_str]

                    # Chercher les perks dans l'item
                    if "perks" in item_def:
                        for perk in item_def["perks"]:
                            perk_hash = str(perk.get("perkHash", ""))

                            # Chercher le perk dans DestinySandboxPerkDefinition
                            if perk_hash in sandboxperk_data:
                                perk_def = sandboxperk_data[perk_hash].get("displayProperties", {})
                                enriched_item.update({
                                    "perkHash": perk_hash,
                                    "name": perk_def.get("name", ""),
                                    "description": perk_def.get("description", ""),
                                    "icon": perk_def.get("icon", None),
                                })
                                break  # Ne prendre que le premier perk

                enriched_items.append(enriched_item)

            tier["items"] = enriched_items

    return artefact_data


def enrich_for_language(lang):
    """Enrichit les données pour une langue donnée"""
    print(f"\n{'='*60}")
    print(f"🌐 ENRICHISSEMENT POUR: {lang.upper()}")
    print(f"{'='*60}")

    # Charger les données sources
    print("📥 Chargement des données sources...")
    setarmor_data = load_json(get_localized_path(SETARMOR_DEFINITIONS_FILE, lang))
    sandboxperk_data = load_json(get_localized_path(SANDBOXPERK_DEFINITIONS_FILE, lang))
    item_data = load_json(get_localized_path(ITEM_DEFINITIONS_FILE, lang))
    artefact_data = load_json(get_localized_path(ARTEFACT_DEFINITIONS_FILE, lang))
    collectible_data = load_json(get_localized_path(COLLECTIBLE_DEFINITIONS_FILE, lang))

    if not all([setarmor_data, sandboxperk_data, item_data, artefact_data, collectible_data]):
        print(f"❌ [{lang.upper()}] Impossible de charger toutes les données sources")
        return False

    print(f"✅ [{lang.upper()}] Données sources chargées")

    # Enrichir les sets d'armure
    print(f"⚙️  [{lang.upper()}] Enrichissement des sets d'armure...")
    enriched_setarmor = enrich_setarmor(setarmor_data, sandboxperk_data, item_data, collectible_data, lang)

    output_path = get_localized_path(SETARMOR_ENRICHED_FILE, lang)
    if save_json(enriched_setarmor, output_path):
        print(f"✅ [{lang.upper()}] Sets enrichis: {get_relative_path(output_path)}")
    else:
        print(f"❌ [{lang.upper()}] Échec de l'enrichissement des sets")
        return False

    # Enrichir les artefacts
    print(f"⚙️  [{lang.upper()}] Enrichissement des artefacts...")
    enriched_artefact = enrich_artefact(artefact_data, sandboxperk_data, item_data)

    output_path = get_localized_path(ARTEFACT_ENRICHED_FILE, lang)
    if save_json(enriched_artefact, output_path):
        print(f"✅ [{lang.upper()}] Artefacts enrichis: {get_relative_path(output_path)}")
    else:
        print(f"❌ [{lang.upper()}] Échec de l'enrichissement des artefacts")
        return False

    return True


def enrich_armor_sets(languages=None):
    """
    Point d'entrée principal pour l'enrichissement

    Args:
        languages: Liste des langues à enrichir. Si None, enrichit toutes les langues supportées.
    """
    if languages is None:
        languages = SUPPORTED_LANGUAGES

    print("=" * 60)
    print("🔧 ENRICHISSEMENT DES DONNÉES (MULTILINGUE)")
    print("=" * 60)
    print(f"Langues à enrichir: {', '.join(lang.upper() for lang in languages)}")

    results = {}
    for lang in languages:
        results[lang] = enrich_for_language(lang)

    print("\n" + "=" * 60)
    print("📊 RÉSUMÉ GLOBAL")
    print("=" * 60)

    for lang, success in results.items():
        status = "✅" if success else "❌"
        print(f"{status} {lang.upper()}: {'Succès' if success else 'Échec'}")

    all_success = all(results.values())

    if all_success:
        print("\n✅ ENRICHISSEMENT TERMINÉ AVEC SUCCÈS")
    else:
        print("\n⚠️  CERTAINS ENRICHISSEMENTS ONT ÉCHOUÉ")

    print("=" * 60)

    return all_success


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description='Enrichit les données d\'armures et artefacts')
    parser.add_argument(
        '--lang',
        nargs='+',
        choices=SUPPORTED_LANGUAGES,
        help='Langues à enrichir (par défaut: toutes)'
    )

    args = parser.parse_args()

    success = enrich_armor_sets(args.lang)
    sys.exit(0 if success else 1)