import json

def indent_json(input_file_path, output_file_path):
    # Lire le fichier JSON
    with open(input_file_path, 'r', encoding='utf-8') as input_file:
        data = json.load(input_file)

    # Écrire le fichier JSON avec une indentation de 4 espaces
    with open(output_file_path, 'w', encoding='utf-8') as output_file:
        json.dump(data, output_file, indent=4, ensure_ascii=False)

# Exemple d'utilisation
indent_json(r'../../../data/en/artefact_definitions_enriched.json', r'../../../data/en/artefact_definitions_enriched.json')