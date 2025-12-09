import json
import requests
import os

from Scripts.ApiKey import bungie_api

HEADERS = {
    'X-API-Key': bungie_api
}

# Liste des définitions à télécharger
manifestlist = {
    "DestinyInventoryItemDefinition": "item_definitions",
    "DestinyTraitDefinition": "trait_definitions",
    "DestinyBreakerTypeDefinition": "breaker_definitions",
    "DestinyDamageTypeDefinition": "damagetype_definitions",
    "DestinyActivityModifierDefinition": "modifier_definitions",
    "DestinyEquipableItemSetDefinition": "setarmor_definitions",
    "DestinySandboxPerkDefinition": "sandboxperk_definitions",
    "DestinyArtifactDefinition": "artefact_definitions",
    "DestinyIconDefinition": "icon_definition"
}

# Dossier de destination
data_dir = '../data'
os.makedirs(data_dir, exist_ok=True)

# Liste des clés à exclure
keys_to_exclude = ["uiItemDisplayStyle", "displaySource", "action", "equippingBlock",
                   "translationBlock", "preview", "quality", "acquireRewardSiteHash",
                   "acquireUnlockHash", "doesPostmasterPullHaveSideEffects", "nonTransferrable",
                   "tooltipNotifications", "backgroundColor", "crafting",
                   "stats", "investmentStats", "allowActions",
                   "nonTransferrable", "isWrapper", "equippable",
                   "traitIds", "traitHashes", "index",
                   "redacted", "blacklisted", "iconWatermark",
                   "iconWatermarkShelved", "iconWatermarkFeatured",
                   "isFeaturedItem", "isHolofoil", "isAdept",
                   "flavorText", "inventory"
                   ]


def has_any_icon_field(data):
    """
    Vérifie si l'élément possède au moins un des champs d'icône.
    Retourne True si au moins un champ existe (même vide).
    """
    icon_fields = [
        'foreground',
        'background',
        'secondaryBackground',
        'specialBackground',
        'highResForeground'
    ]

    for field in icon_fields:
        if field in data:
            return True

    return False


def all_icon_fields_empty(data):
    """
    Vérifie si TOUS les champs d'icône présents sont vides.
    Retourne True seulement si au moins un champ existe ET que tous sont vides.
    """
    icon_fields = [
        'foreground',
        'background',
        'secondaryBackground',
        'specialBackground',
        'highResForeground'
    ]

    found_fields = []
    for field in icon_fields:
        if field in data:
            found_fields.append(field)

    # Si aucun champ trouvé, on retourne False (on garde l'item)
    if not found_fields:
        return False

    # Si au moins un champ existe, vérifier s'ils sont TOUS vides
    for field in found_fields:
        if data[field] and data[field].strip():
            return False  # Au moins un champ non vide trouvé

    return True  # Tous les champs présents sont vides


def clean_data(data, definition_type=None):
    if isinstance(data, dict):
        # Supprimer les clés indésirables
        for key in keys_to_exclude:
            if key in data:
                del data[key]

        # Vérifier et supprimer l'élément si 'hasIcon' est False ou 'name' vide
        # 🚨 Sauf si on est dans setarmor_definitions
        if definition_type != "setarmor_definitions":
            if 'displayProperties' in data:
                display_props = data['displayProperties']
                if ('hasIcon' in display_props and display_props['hasIcon'] is False) or \
                        ('name' in display_props and not display_props['name']):
                    return None

            # Vérifier si des champs d'icône existent ET sont tous vides
            if all_icon_fields_empty(data):
                return None

        # Appliquer récursivement le nettoyage aux sous-éléments
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
        return [clean_data(item, definition_type) for item in data if clean_data(item, definition_type) is not None]

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
            # 👇 on passe le type de fichier pour adapter le nettoyage
            cleaned_data = clean_data(data, file_name)
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(cleaned_data, f, ensure_ascii=False)
            print(f"{definition_key} enregistré sous {file_path}.")
        except ValueError:
            print(f"Erreur lors de la conversion en JSON pour {definition_key}. Contenu de la réponse : {r.text[:500]}")

print("Téléchargement et nettoyage terminés.")