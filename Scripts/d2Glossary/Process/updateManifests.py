"""
updateManifests.py - Téléchargement et nettoyage des manifests Bungie (multilingue)
Utilise une approche WHITELIST : on ne garde que les clés explicitement listées
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
    get_whitelist_for_definition
)
from Utils.ApiKey import bungie_api

HEADERS = {'X-API-Key': bungie_api}
MANIFEST_URL = 'https://www.bungie.net/platform/Destiny2/Manifest'

# Mapping des codes de langue Bungie
BUNGIE_LANG_CODES = {
    "fr": "fr",
    "en": "en"
}


def extract_whitelisted_data(data: dict, whitelist: list[str], current_path: str = "") -> dict | None:
    """
    Extrait uniquement les données whitelistées d'un dictionnaire

    Args:
        data: Données source
        whitelist: Liste des chemins de clés à conserver
        current_path: Chemin actuel (pour la récursion)

    Returns:
        Dictionnaire nettoyé ou None si vide/invalide
    """
    if not isinstance(data, dict):
        return data

    result = {}

    for key, value in data.items():
        # Construire le chemin complet de la clé
        full_path = f"{current_path}.{key}" if current_path else key

        # Vérifier si cette clé ou un de ses enfants est dans la whitelist
        key_is_whitelisted = any(
            # Clé exacte
            full_path == w or
            # Clé parente (ex: "displayProperties" autorise "displayProperties.name")
            w.startswith(full_path + ".") or
            # Clé enfant (ex: "displayProperties.name" autorise "displayProperties")
            full_path.startswith(w + ".")
            for w in whitelist
        )

        # Vérifier aussi si la clé elle-même est directement whitelistée
        direct_match = full_path in whitelist

        if key_is_whitelisted or direct_match:
            if isinstance(value, dict):
                # Récursion pour les objets imbriqués
                cleaned_value = extract_whitelisted_data(value, whitelist, full_path)
                if cleaned_value:  # Ne pas ajouter les dicts vides
                    result[key] = cleaned_value
            elif isinstance(value, list):
                # Traiter les listes
                cleaned_list = []
                for i, item in enumerate(value):
                    if isinstance(item, dict):
                        cleaned_item = extract_whitelisted_data(item, whitelist, full_path)
                        if cleaned_item:
                            cleaned_list.append(cleaned_item)
                    else:
                        cleaned_list.append(item)
                if cleaned_list:
                    result[key] = cleaned_list
            else:
                # Valeur simple
                result[key] = value

    return result if result else None


def should_keep_entry(data: dict, definition_type: str) -> bool:
    """
    Détermine si une entrée doit être conservée

    Args:
        data: Données de l'entrée
        definition_type: Type de définition

    Returns:
        True si l'entrée doit être conservée
    """
    # Vérifications spécifiques selon le type
    if definition_type == "setarmor_definitions":
        # Pour les sets d'armure, pas de vérification d'icône
        return True

    # Vérifications standard
    display_props = data.get('displayProperties', {})

    # Doit avoir un nom non vide
    if not display_props.get('name'):
        return False

    # Doit avoir une icône (sauf exception)
    if display_props.get('hasIcon') is False:
        return False

    return True


def clean_data(data: dict, definition_type: str) -> dict | None:
    """
    Nettoie les données du manifest en utilisant la whitelist

    Args:
        data: Données brutes du manifest
        definition_type: Type de définition (pour la whitelist appropriée)

    Returns:
        Dictionnaire nettoyé
    """
    if not isinstance(data, dict):
        return data

    # Récupérer la whitelist pour ce type
    whitelist = get_whitelist_for_definition(definition_type)

    result = {}

    for entry_id, entry_data in data.items():
        if not isinstance(entry_data, dict):
            continue

        # Vérifier si l'entrée doit être conservée
        if not should_keep_entry(entry_data, definition_type):
            continue

        # Extraire uniquement les données whitelistées
        cleaned_entry = extract_whitelisted_data(entry_data, whitelist)

        if cleaned_entry:
            result[entry_id] = cleaned_entry

    return result


def download_manifest(definition_key: str, file_name: str, lang: str = "fr") -> bool:
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
        definition_type = file_name.replace(".json", "")

        print(f"📥 [{lang.upper()}] Téléchargement de {definition_key}...")
        r = requests.get(full_url, headers=HEADERS)
        r.raise_for_status()

        # Nettoyer avec la whitelist
        data = r.json()
        original_count = len(data) if isinstance(data, dict) else 0

        cleaned_data = clean_data(data, definition_type)
        final_count = len(cleaned_data) if isinstance(cleaned_data, dict) else 0

        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(cleaned_data, f, ensure_ascii=False)

        print(f"✅ [{lang.upper()}] {definition_key} enregistré: {get_relative_path(file_path)}")
        print(f"   📊 {final_count}/{original_count} entrées conservées (whitelist)")
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
    print("📦 MISE À JOUR DES MANIFESTS BUNGIE (WHITELIST)")
    print("=" * 60)
    print(f"Langues à télécharger: {', '.join(lang.upper() for lang in languages)}")
    print(f"Mode: WHITELIST (on ne garde que les clés essentielles)")
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