"""
updateManifests.py - Téléchargement et nettoyage des manifests Bungie (multilingue)
Utilise une approche WHITELIST : on ne garde que les clés explicitement listées
Si aucune whitelist n'est définie, on garde toutes les données
"""
import json
import requests
from pathlib import Path
import sys

# Ajouter le dossier parent au path pour les imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from Utils.paths import (
    DATA_DIR, MANIFEST_LIST, SUPPORTED_LANGUAGES,
    ensure_data_dirs, get_relative_path, get_localized_path,
    get_whitelist_for_definition, is_key_whitelisted
)
from Utils.ApiKey import bungie_api

HEADERS = {'X-API-Key': bungie_api}
MANIFEST_URL = 'https://www.bungie.net/platform/Destiny2/Manifest'

# Mapping des codes de langue Bungie
BUNGIE_LANG_CODES = {
    "fr": "fr",
    "en": "en"
}

# Types de définitions qui n'ont PAS de displayProperties standard
# et doivent ignorer la vérification nom/icône
SKIP_DISPLAY_CHECK = [
    "setarmor_definitions",
    "item_category_definitions",
    "socket_type_definitions",
    "socket_category_definitions",
    "icon_definition",
    "collectible_definitions",
]


def filter_by_whitelist(data: dict, whitelist: list[str]) -> dict:
    """
    Filtre un dictionnaire en ne gardant que les clés whitelistées

    Args:
        data: Dictionnaire à filtrer
        whitelist: Liste des clés autorisées

    Returns:
        Dictionnaire filtré
    """
    if not isinstance(data, dict):
        return data

    filtered = {}

    for key, value in data.items():
        # Vérifier si cette clé est dans la whitelist
        if key in whitelist:
            # Si c'est un dict ou une liste, on le garde tel quel
            # (la whitelist autorise l'objet complet)
            filtered[key] = value
        elif isinstance(value, dict):
            # Vérifier si des sous-clés sont whitelistées
            sub_filtered = {}
            for sub_key, sub_value in value.items():
                full_path = f"{key}.{sub_key}"
                if is_key_whitelisted(full_path, whitelist):
                    sub_filtered[sub_key] = sub_value

            if sub_filtered:
                filtered[key] = sub_filtered

    return filtered


def should_skip_display_check(definition_type: str) -> bool:
    """
    Vérifie si on doit ignorer la vérification displayProperties pour ce type

    Args:
        definition_type: Type de définition

    Returns:
        True si on doit ignorer la vérification
    """
    clean_type = definition_type.replace(".json", "") if definition_type else ""
    return clean_type in SKIP_DISPLAY_CHECK


def clean_data(data, definition_type=None):
    """
    Nettoie récursivement les données du manifest en utilisant la whitelist

    Args:
        data: Données à nettoyer
        definition_type: Type de définition (ex: "item_definitions")

    Returns:
        Données nettoyées
    """
    # Récupérer la whitelist pour ce type
    whitelist = get_whitelist_for_definition(definition_type) if definition_type else None

    # Vérifier si on doit ignorer la vérification displayProperties
    skip_display = should_skip_display_check(definition_type)

    if isinstance(data, dict):
        # Si c'est le niveau racine (dict de hash -> item), traiter chaque item
        cleaned = {}

        for key, value in data.items():
            if isinstance(value, dict):
                # C'est un item individuel

                # Vérifications de base (items sans nom/icône)
                # SAUF pour les types qui n'ont pas de displayProperties standard
                if not skip_display and 'displayProperties' in value:
                    display_props = value['displayProperties']
                    # Ignorer les items sans nom ou sans icône
                    if display_props.get('hasIcon') is False or not display_props.get('name'):
                        continue

                # Si pas de whitelist, garder tout l'item
                if whitelist is None:
                    cleaned[key] = value
                else:
                    # Appliquer la whitelist
                    filtered_item = filter_by_whitelist(value, whitelist)
                    if filtered_item:  # Ne garder que si pas vide
                        cleaned[key] = filtered_item
            else:
                # Garder les autres types de données
                cleaned[key] = value

        return cleaned

    elif isinstance(data, list):
        # Pour les listes, nettoyer chaque élément
        return [clean_data(item, definition_type) for item in data if item is not None]

    return data


def download_manifest(definition_key, file_name, lang="fr"):
    """Télécharge un fichier du manifest pour une langue donnée"""
    try:
        # Requête pour obtenir le manifeste
        response = requests.get(MANIFEST_URL, headers=HEADERS)
        manifest_data = response.json()

        # Extraire les chemins dans la langue demandée
        bungie_lang = BUNGIE_LANG_CODES.get(lang, "fr")
        lang_manifest_paths = manifest_data['Response']['jsonWorldComponentContentPaths'][bungie_lang]

        if definition_key not in lang_manifest_paths:
            print(f"⚠️  {definition_key} non trouvé dans le manifest [{lang.upper()}]")
            return False

        # Télécharger le fichier
        full_url = "https://www.bungie.net" + lang_manifest_paths[definition_key]
        file_path = get_localized_path(file_name, lang)

        print(f"📥 [{lang.upper()}] Téléchargement de {definition_key}...")
        r = requests.get(full_url, headers=HEADERS)
        r.raise_for_status()

        # Déterminer le type de définition pour la whitelist
        definition_type = file_name.replace(".json", "")

        # Vérifier si une whitelist existe
        whitelist = get_whitelist_for_definition(definition_type)
        if whitelist is None:
            print(f"   ℹ️  Pas de whitelist pour {definition_type}, conservation de toutes les clés")
        else:
            print(f"   🔧 Application de la whitelist ({len(whitelist)} clés autorisées)")

        # Nettoyer et sauvegarder
        data = r.json()
        cleaned_data = clean_data(data, definition_type)

        # Compter les items avant/après pour le log
        original_count = len(data) if isinstance(data, dict) else 0
        cleaned_count = len(cleaned_data) if isinstance(cleaned_data, dict) else 0

        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(cleaned_data, f, ensure_ascii=False)

        print(f"✅ [{lang.upper()}] {definition_key} enregistré: {get_relative_path(file_path)}")
        print(f"   📊 {cleaned_count}/{original_count} items conservés")
        return True

    except requests.RequestException as e:
        print(f"❌ [{lang.upper()}] Erreur réseau pour {definition_key}: {e}")
        return False
    except (ValueError, KeyError) as e:
        print(f"❌ [{lang.upper()}] Erreur de parsing pour {definition_key}: {e}")
        return False
    except Exception as e:
        print(f"❌ [{lang.upper()}] Erreur inattendue pour {definition_key}: {e}")
        return False


def update_manifests(languages=None):
    """
    Point d'entrée principal pour la mise à jour des manifests

    Args:
        languages: Liste des langues à télécharger. Si None, télécharge toutes les langues supportées.
    """
    if languages is None:
        languages = SUPPORTED_LANGUAGES

    print("=" * 60)
    print("📦 MISE À JOUR DES MANIFESTS BUNGIE (MULTILINGUE)")
    print("=" * 60)
    print(f"Langues à télécharger: {', '.join(lang.upper() for lang in languages)}")
    print()

    ensure_data_dirs()

    total_success = 0
    total_count = len(MANIFEST_LIST) * len(languages)

    results_by_lang = {}

    for lang in languages:
        print(f"\n{'='*60}")
        print(f"🌐 LANGUE: {lang.upper()}")
        print(f"{'='*60}")

        lang_success = 0

        for definition_key, file_name in MANIFEST_LIST.items():
            if download_manifest(definition_key, file_name, lang):
                lang_success += 1
                total_success += 1

        results_by_lang[lang] = {
            "success": lang_success,
            "total": len(MANIFEST_LIST)
        }

        print(f"\n✅ [{lang.upper()}] Téléchargement terminé: {lang_success}/{len(MANIFEST_LIST)} fichiers")

    print("\n" + "=" * 60)
    print("📊 RÉSUMÉ GLOBAL")
    print("=" * 60)

    for lang, results in results_by_lang.items():
        status = "✅" if results["success"] == results["total"] else "⚠️"
        print(f"{status} {lang.upper()}: {results['success']}/{results['total']} fichiers")

    print(f"\n✅ Total: {total_success}/{total_count} fichiers téléchargés")
    print("=" * 60)

    return total_success == total_count


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description='Télécharge les manifests Bungie')
    parser.add_argument(
        '--lang',
        nargs='+',
        choices=SUPPORTED_LANGUAGES,
        help='Langues à télécharger (par défaut: toutes)'
    )

    args = parser.parse_args()

    success = update_manifests(args.lang)
    sys.exit(0 if success else 1)