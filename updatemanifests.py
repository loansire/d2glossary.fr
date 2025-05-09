import json
import requests
import os
import ApiKey as APIKey

# Clé API de Bungie à insérer ici (nécessaire pour les requêtes)
API_KEY = APIKey.bungie_api
HEADERS = {
    'X-API-Key': API_KEY
}

# Liste des définitions à télécharger
manifestlist = {
    "DestinyInventoryItemDefinition": "item_definitions",
    "DestinyTraitDefinition": "trait_definitions",
    "DestinyBreakerTypeDefinition": "breaker_definitions",
    "DestinyDamageTypeDefinition": "damagetype_definitions",
    "DestinyActivityModifierDefinition": "modifier_definitions"
}

# Dossier de destination
data_dir = 'data'
os.makedirs(data_dir, exist_ok=True)

# Fonction pour nettoyer les items avec "hasIcon": false
def clean_data(data):
    if isinstance(data, dict):
        # Vérifier et supprimer l'élément si 'hasIcon' est False
        if 'hasIcon' in data and data['hasIcon'] is False:
            return None

        # Vérifier si 'displayProperties' existe et si 'name' ou 'description' sont vides
        if 'displayProperties' in data:
            if ('name' in data['displayProperties'] and not data['displayProperties']['name']) or \
               ('description' in data['displayProperties'] and not data['displayProperties']['description']):
                return None  # Supprimer l'élément entier si 'name' ou 'description' sont vides

        # Appliquer récursivement le nettoyage aux sous-éléments
        for key in data:
            data[key] = clean_data(data[key])

    elif isinstance(data, list):
        # Applique récursivement le nettoyage aux éléments de la liste
        return [clean_data(item) for item in data]

    return data

# Étape 1 : Requête pour obtenir le manifeste
manifest_url = 'https://www.bungie.net/platform/Destiny2/Manifest'
response = requests.get(manifest_url, headers=HEADERS)
manifest_data = response.json()

# Étape 2 : Extraire les chemins en français
try:
    fr_manifest_paths = manifest_data['Response']['jsonWorldComponentContentPaths']['fr']
except KeyError:
    raise Exception("Les chemins français ne sont pas disponibles dans le manifeste.")

# Étape 3 : Télécharger les fichiers spécifiés avec noms personnalisés
for definition_key, file_name in manifestlist.items():
    if definition_key in fr_manifest_paths:
        full_url = "https://www.bungie.net" + fr_manifest_paths[definition_key]
        file_path = os.path.join(data_dir, f"{file_name}.json")
        print(f"Téléchargement de {definition_key} depuis {full_url}...")
        r = requests.get(full_url, headers=HEADERS)
        try:
            data = r.json()
            # Appliquer le nettoyage avant de sauvegarder
            cleaned_data = clean_data(data)
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(cleaned_data, f, ensure_ascii=False)  # Format compact sans indentation
            print(f"{definition_key} enregistré sous {file_path}.")
        except ValueError:
            print(f"Erreur lors de la conversion en JSON pour {definition_key}. Contenu de la réponse : {r.text[:500]}")

print("Téléchargement et nettoyage terminés.")
