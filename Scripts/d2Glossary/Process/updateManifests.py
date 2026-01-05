"""
updateManifests.py - Téléchargement et nettoyage des manifests Bungie
"""
import json
import requests
from pathlib import Path
import sys

# Ajouter le dossier parent au path pour les imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from Utils.paths import (
    DATA_DIR, MANIFEST_LIST, KEYS_TO_EXCLUDE,
    ensure_data_dir, get_relative_path
)
from Utils.ApiKey import bungie_api

HEADERS = {'X-API-Key': bungie_api}
MANIFEST_URL = 'https://www.bungie.net/platform/Destiny2/Manifest'


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


def download_manifest(definition_key, file_name):
    """Télécharge un fichier du manifest et le nettoie"""
    try:
        # Requête pour obtenir le manifeste
        response = requests.get(MANIFEST_URL, headers=HEADERS)
        manifest_data = response.json()

        # Extraire les chemins en français
        fr_manifest_paths = manifest_data['Response']['jsonWorldComponentContentPaths']['fr']

        if definition_key not in fr_manifest_paths:
            print(f"⚠️  {definition_key} non trouvé dans le manifest")
            return False

        # Télécharger le fichier
        full_url = "https://www.bungie.net" + fr_manifest_paths[definition_key]
        file_path = DATA_DIR / f"{file_name}.json"

        print(f"📥 Téléchargement de {definition_key}...")
        r = requests.get(full_url, headers=HEADERS)
        r.raise_for_status()

        # Nettoyer et sauvegarder
        data = r.json()
        cleaned_data = clean_data(data, file_name)

        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(cleaned_data, f, ensure_ascii=False)

        print(f"✅ {definition_key} enregistré: {get_relative_path(file_path)}")
        return True

    except requests.RequestException as e:
        print(f"❌ Erreur réseau pour {definition_key}: {e}")
        return False
    except (ValueError, KeyError) as e:
        print(f"❌ Erreur de parsing pour {definition_key}: {e}")
        return False
    except Exception as e:
        print(f"❌ Erreur inattendue pour {definition_key}: {e}")
        return False


def update_manifests():
    """Point d'entrée principal pour la mise à jour des manifests"""
    print("=" * 60)
    print("📦 MISE À JOUR DES MANIFESTS BUNGIE")
    print("=" * 60)

    ensure_data_dir()

    success_count = 0
    total_count = len(MANIFEST_LIST)

    for definition_key, file_name in MANIFEST_LIST.items():
        if download_manifest(definition_key, file_name):
            success_count += 1
        print()

    print("=" * 60)
    print(f"✅ Téléchargement terminé: {success_count}/{total_count} fichiers")
    print("=" * 60)

    return success_count == total_count


if __name__ == "__main__":
    success = update_manifests()
    sys.exit(0 if success else 1)