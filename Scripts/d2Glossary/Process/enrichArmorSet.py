"""
enrichArmorSet.py - Enrichissement des données d'armures et artefacts (multilingue)
"""
import json
from pathlib import Path
import sys

# Ajouter le dossier parent au path pour les imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from Utils.paths import (
    SUPPORTED_LANGUAGES, get_localized_path, get_relative_path,
    SETARMOR_DEFINITIONS_FILE, SANDBOXPERK_DEFINITIONS_FILE,
    ITEM_DEFINITIONS_FILE, ARTEFACT_DEFINITIONS_FILE,
    SETARMOR_ENRICHED_FILE, ARTEFACT_ENRICHED_FILE
)


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


def enrich_setarmor(setarmor_data, sandboxperk_data, item_data):
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

        # Enrichir les setItems directement
        if "setItems" in set_info:
            enriched_items = []
            for item_hash in set_info["setItems"]:
                item_hash_str = str(item_hash)
                if item_hash_str in item_data:
                    item_def = item_data[item_hash_str].get("displayProperties", {})
                    enriched_items.append({
                        "hash": item_hash,
                        "name": item_def.get("name", ""),
                        "icon": item_def.get("icon", None),
                    })
            set_info["setItems"] = enriched_items

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

    if not all([setarmor_data, sandboxperk_data, item_data, artefact_data]):
        print(f"❌ [{lang.upper()}] Impossible de charger toutes les données sources")
        return False

    print(f"✅ [{lang.upper()}] Données sources chargées")

    # Enrichir les sets d'armure
    print(f"⚙️  [{lang.upper()}] Enrichissement des sets d'armure...")
    enriched_setarmor = enrich_setarmor(setarmor_data, sandboxperk_data, item_data)

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