"""
enrichSubclass.py - Enrichissement des données de subclass
Filtre item_definitions pour les plugCategoryIdentifier de subclass,
puis enrichit avec les descriptions de sandboxperk_definitions.
"""
import json
from pathlib import Path
import sys

# Ajouter le dossier parent au path pour les imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from Utils.paths import (
    SUPPORTED_LANGUAGES, get_localized_path, get_relative_path,
    ITEM_DEFINITIONS_FILE, SANDBOXPERK_DEFINITIONS_FILE,
    SUBCLASS_ENRICHED_FILE
)


# =========================================================================
# CONFIGURATION
# =========================================================================

# Tous les plugCategoryIdentifier liés aux subclasses
SUBCLASS_PLUG_CATEGORIES = [
    # Arc
    "hunter.arc.aspects", "hunter.arc.class_abilities", "hunter.arc.melee",
    "hunter.arc.movement", "hunter.arc.supers",
    "titan.arc.aspects", "titan.arc.class_abilities", "titan.arc.melee",
    "titan.arc.movement", "titan.arc.supers",
    "warlock.arc.aspects", "warlock.arc.class_abilities", "warlock.arc.melee",
    "warlock.arc.movement", "warlock.arc.supers",
    "shared.arc.fragments", "shared.arc.grenades",
    # Void
    "hunter.void.aspects", "hunter.void.class_abilities", "hunter.void.melee",
    "hunter.void.movement", "hunter.void.supers",
    "titan.void.aspects", "titan.void.class_abilities", "titan.void.melee",
    "titan.void.movement", "titan.void.supers",
    "warlock.void.aspects", "warlock.void.class_abilities", "warlock.void.melee",
    "warlock.void.movement", "warlock.void.supers",
    "shared.void.fragments", "shared.void.grenades",
    # Solar
    "hunter.solar.aspects", "hunter.solar.class_abilities", "hunter.solar.melee",
    "hunter.solar.movement", "hunter.solar.supers",
    "titan.solar.aspects", "titan.solar.class_abilities", "titan.solar.melee",
    "titan.solar.movement", "titan.solar.supers",
    "warlock.solar.aspects", "warlock.solar.class_abilities", "warlock.solar.melee",
    "warlock.solar.movement", "warlock.solar.supers",
    "shared.solar.fragments", "shared.solar.grenades",
    # Stasis
    "hunter.stasis.totems", "hunter.stasis.class_abilities", "hunter.stasis.melee",
    "hunter.stasis.movement", "hunter.stasis.supers",
    "titan.stasis.totems", "titan.stasis.class_abilities", "titan.stasis.melee",
    "titan.stasis.movement", "titan.stasis.supers",
    "warlock.stasis.totems", "warlock.stasis.class_abilities", "warlock.stasis.melee",
    "warlock.stasis.movement", "warlock.stasis.supers",
    "shared.stasis.trinkets", "shared.stasis.grenades",
    # Strand
    "hunter.strand.aspects", "hunter.strand.class_abilities", "hunter.strand.melee",
    "hunter.strand.movement", "hunter.strand.supers",
    "titan.strand.aspects", "titan.strand.class_abilities", "titan.strand.melee",
    "titan.strand.movement", "titan.strand.supers",
    "warlock.strand.aspects", "warlock.strand.class_abilities", "warlock.strand.melee",
    "warlock.strand.movement", "warlock.strand.supers",
    "shared.strand.fragments", "shared.strand.grenades",
    # prism
    "hunter.prism.aspects", "hunter.prism.class_abilities", "hunter.prism.melee",
    "hunter.prism.movement", "hunter.prism.supers", "hunter.prism.grenades",
    "titan.prism.aspects", "titan.prism.class_abilities", "titan.prism.melee",
    "titan.prism.movement", "titan.prism.supers", "titan.prism.grenades",
    "warlock.prism.aspects", "warlock.prism.class_abilities", "warlock.prism.melee",
    "warlock.prism.movement", "warlock.prism.supers", "warlock.prism.grenades",
    "shared.prism.fragments",
    "hunter.prism.prism_grenade", "titan.prism.prism_grenade", "warlock.prism.prism_grenade",
]


# =========================================================================
# FONCTIONS UTILITAIRES (réutilisées depuis enrichArmorSet.py)
# =========================================================================

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


# =========================================================================
# ENRICHISSEMENT
# =========================================================================

def enrich_subclass(item_data, sandboxperk_data):
    """
    Filtre et enrichit les items de subclass.

    Pour chaque item dont plug.plugCategoryIdentifier est dans SUBCLASS_PLUG_CATEGORIES :
    - On garde l'item tel quel (hash, displayProperties, plug)
    - On cherche le perkHash dans perks[]
    - On remplace la description par celle du sandboxperk correspondant

    Returns:
        dict: {item_hash: item_enrichi, ...}
    """
    enriched = {}
    enriched_count = 0
    skipped_no_perk = 0

    for item_hash, item in item_data.items():
        # Vérifier si c'est un item de subclass
        plug = item.get("plug")
        if not plug:
            continue

        plug_cat_id = plug.get("plugCategoryIdentifier", "")
        if plug_cat_id not in SUBCLASS_PLUG_CATEGORIES:
            continue

        # Copier l'item tel quel
        enriched_item = {
            "hash": int(item_hash),
            "displayProperties": dict(item.get("displayProperties", {})),
            "plug": {
                "plugCategoryIdentifier": plug_cat_id,
            },
        }

        # Chercher le perkHash et récupérer la description du sandboxperk
        perks = item.get("perks", [])
        for perk_entry in perks:
            perk_hash = str(perk_entry.get("perkHash", ""))
            if perk_hash and perk_hash in sandboxperk_data:
                sandbox_desc = sandboxperk_data[perk_hash].get("displayProperties", {}).get("description", "")

                if sandbox_desc:
                    enriched_item["displayProperties"]["description"] = sandbox_desc

                enriched_item["perkHash"] = perk_hash
                enriched_count += 1
                break
        else:
            skipped_no_perk += 1

        enriched[item_hash] = enriched_item

    total = len(enriched)
    print(f"   📊 {total} items de subclass trouvés")
    print(f"   ✅ {enriched_count} enrichis avec sandboxperk")
    if skipped_no_perk:
        print(f"   ℹ️  {skipped_no_perk} sans match sandboxperk (description item conservée)")

    return enriched


# =========================================================================
# POINT D'ENTRÉE
# =========================================================================

def enrich_subclass_for_language(lang):
    """Enrichit les données de subclass pour une langue donnée"""
    print(f"\n⚙️  [{lang.upper()}] Enrichissement des subclass...")

    item_data = load_json(get_localized_path(ITEM_DEFINITIONS_FILE, lang))
    sandboxperk_data = load_json(get_localized_path(SANDBOXPERK_DEFINITIONS_FILE, lang))

    if not item_data or not sandboxperk_data:
        print(f"❌ [{lang.upper()}] Impossible de charger les données sources")
        return False

    enriched = enrich_subclass(item_data, sandboxperk_data)

    output_path = get_localized_path(SUBCLASS_ENRICHED_FILE, lang)
    if save_json(enriched, output_path):
        print(f"✅ [{lang.upper()}] Subclass enrichis: {get_relative_path(output_path)}")
        return True
    else:
        print(f"❌ [{lang.upper()}] Échec de l'enrichissement des subclass")
        return False


def enrich_subclasses(languages=None):
    """
    Point d'entrée principal pour l'enrichissement des subclass.

    Args:
        languages: Liste des langues. Si None, toutes les langues supportées.
    """
    if languages is None:
        languages = SUPPORTED_LANGUAGES

    print("\n" + "-" * 40)
    print("🔮 ENRICHISSEMENT DES SUBCLASS")
    print("-" * 40)

    results = {}
    for lang in languages:
        results[lang] = enrich_subclass_for_language(lang)

    all_success = all(results.values())

    for lang, success in results.items():
        status = "✅" if success else "❌"
        print(f"   {status} {lang.upper()}: {'Succès' if success else 'Échec'}")

    return all_success


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description='Enrichit les données de subclass')
    parser.add_argument(
        '--lang',
        nargs='+',
        choices=SUPPORTED_LANGUAGES,
        help='Langues à enrichir (par défaut: toutes)'
    )

    args = parser.parse_args()
    success = enrich_subclasses(args.lang)
    sys.exit(0 if success else 1)