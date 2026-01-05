import json

def afficher_item_type_display_name_avec_ids(fichier_json):
    # Charger le fichier JSON
    with open(fichier_json, 'r', encoding='utf-8') as f:
        data = json.load(f)

    # Créer un dictionnaire pour stocker les itemTypeDisplayName et leurs IDs associés
    item_type_dict = {}
    for key, entry in data.items():
        item_type = entry.get('itemTypeDisplayName')
        if item_type:
            if item_type not in item_type_dict:
                item_type_dict[item_type] = []
            item_type_dict[item_type].append(key)

    # Afficher les itemTypeDisplayName uniques avec leurs IDs associés
    for item_type, ids in item_type_dict.items():
        print(f"{item_type}: {', '.join(ids)}")

# Remplacez 'votre_fichier.json' par le chemin vers votre fichier JSON
afficher_item_type_display_name_avec_ids('../../../data/item_definitions.json')