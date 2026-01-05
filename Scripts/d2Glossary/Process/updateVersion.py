"""
updateVersion.py - Mise à jour du fichier version.json
"""
import json
from datetime import datetime
from pathlib import Path
import sys

# Ajouter le dossier parent au path pour les imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from Utils.paths import VERSION_FILE, VERSION_CONFIG, get_relative_path


def update_version():
    """Met à jour le fichier version.json avec la date actuelle"""
    print("=" * 60)
    print("📝 MISE À JOUR DE LA VERSION")
    print("=" * 60)

    # Lire ou créer la structure de base
    if VERSION_FILE.exists():
        try:
            with open(VERSION_FILE, 'r', encoding='utf-8') as f:
                data = json.load(f)
        except json.JSONDecodeError:
            print("⚠️  Fichier version.json corrompu, recréation...")
            data = {}
    else:
        print("ℹ️  Création du fichier version.json...")
        data = {}

    # Mettre à jour avec la structure complète
    now = datetime.now()
    data.update({
        "version": now.strftime('%Y-%m-%d'),
        "lastUpdate": now.strftime('%Y-%m-%dT%H:%M:%SZ'),
        "files": VERSION_CONFIG
    })

    # Sauvegarder
    try:
        with open(VERSION_FILE, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

        print(f"✅ Version mise à jour: {data['version']}")
        print(f"   Dernière MAJ: {data['lastUpdate']}")
        print(f"   Fichier: {get_relative_path(VERSION_FILE)}")
        print("=" * 60)
        return True

    except Exception as e:
        print(f"❌ Erreur d'écriture: {e}")
        print("=" * 60)
        return False


if __name__ == "__main__":
    success = update_version()
    sys.exit(0 if success else 1)