"""
updateManifests.py - Téléchargement et nettoyage des manifests Bungie (multilingue)
"""
import json
import requests
from pathlib import Path
import sys

# Ajouter le dossier parent au path pour les imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from Utils.paths import (
    DATA_DIR, MANIFEST_LIST, KEYS_TO_EXCLUDE, SUPPORTED_LANGUAGES,
    ensure_data_dirs, get_relative_path, get_localized_path
)
from Utils.ApiKey import bungie_api

HEADERS = {'X-API-Key': bungie_api}
MANIFEST_URL = 'https://www.bungie.net/platform/Destiny2/Manifest'

# Mapping des codes de langue Bungie
BUNGIE_LANG_CODES = {
    "fr": "fr",
    "en": "en"
}


def has_any_icon_field(data):
    """Vérifie si l'élément possède au moins un des champs d'icône"""
    icon_fields = ['foreground', 'background', 'secondaryBackground',
                   'specialBackground', 'highResForeground']
    return any(field in data for field in icon_fields)


def all_icon_fields_empty(data):
    """Vérifie si TOUS les champs d'icône présents sont vides"""
    icon_fields = ['foreground', 'background', 'secondaryBackground',
                   'specialBackground', 'highResForeground']

    found_fields = [field for field in icon_fields if field in data]

    if not found_fields:
        return False

    return all(not data[field] or not data[field].strip() for field in found_fields)


def clean_data(data, definition_type=None):
    """Nettoie récursivement les données du manifest"""
    if isinstance(data, dict):
        # Supprimer les clés indésirables
        for key in KEYS_TO_EXCLUDE:
            data.pop(key, None)

        # Vérifications spécifiques (sauf pour setarmor)
        if definition_type != "setarmor_definitions":
            if 'displayProperties' in data:
                display_props = data['displayProperties']
                if (display_props.get('hasIcon') is False or
                        not display_props.get('name')):
                    return None

            if all_icon_fields_empty(data):
                return None

        # Nettoyage récursif
        keys_to_remove = []
        for key, value in data.items():
            cleaned_value = clean_data(value, definition_type)
            if cleaned_value is None:
                keys_to_remove.append(key)
            else:
                data[key] = cleaned_value

        for key in keys_to_remove:
            del data[key]

    elif isinstance(data, list):
        return [clean_data(item, definition_type)
                for item in data
                if clean_data(item, definition_type) is not None]

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

        # Nettoyer et sauvegarder
        data = r.json()
        cleaned_data = clean_data(data, file_name.replace(".json", ""))

        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(cleaned_data, f, ensure_ascii=False)

        print(f"✅ [{lang.upper()}] {definition_key} enregistré: {get_relative_path(file_path)}")
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