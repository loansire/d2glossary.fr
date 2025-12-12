"""
updateVersion.py - Met à jour la version dans version.json
Exécute ce script après avoir mis à jour les fichiers JSON du manifest Bungie
"""

import json
from datetime import datetime
import os

# Chemin vers version.json (dans le dossier data)
VERSION_FILE = '../data/version.json'

def update_version():
    # Lire le fichier actuel
    if os.path.exists(VERSION_FILE):
        with open(VERSION_FILE, 'r', encoding='utf-8') as f:
            data = json.load(f)
    else:
        data = {
            "version": "",
            "lastUpdate": "",
            "files": {
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
        }

    # Mettre à jour la version avec la date du jour
    now = datetime.now()
    data['version'] = now.strftime('%Y-%m-%d')
    data['lastUpdate'] = now.strftime('%Y-%m-%dT%H:%M:%SZ')

    # Sauvegarder
    with open(VERSION_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

    print(f"✅ Version mise à jour: {data['version']}")
    print(f"   Dernière MAJ: {data['lastUpdate']}")

if __name__ == '__main__':
    update_version()