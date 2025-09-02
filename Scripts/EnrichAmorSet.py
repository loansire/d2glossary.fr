import json
import os

# Répertoires
data_dir = "../data"

# Fichiers source
setarmor_file = os.path.join(data_dir, "setarmor_definitions.json")
sandboxperk_file = os.path.join(data_dir, "sandboxperk_definitions.json")
item_file = os.path.join(data_dir, "item_definitions.json")

# Fichier de sortie
enriched_file = os.path.join(data_dir, "setarmor_definitions_enriched.json")

# Charger les JSON
with open(setarmor_file, "r", encoding="utf-8") as f:
    setarmor_data = json.load(f)

with open(sandboxperk_file, "r", encoding="utf-8") as f:
    sandboxperk_data = json.load(f)

with open(item_file, "r", encoding="utf-8") as f:
    item_data = json.load(f)


def enrich_setarmor(data):
    for set_id, set_info in data.items():

        # 🔹 Enrichir les setPerks avec sandboxperk_definitions
        if "setPerks" in set_info:
            for perk in set_info["setPerks"]:
                perk_hash = str(perk["sandboxPerkHash"])
                if perk_hash in sandboxperk_data:
                    perk_def = sandboxperk_data[perk_hash].get("displayProperties", {})
                    perk["displayProperties"] = {
                        "name": perk_def.get("name", ""),
                        "description": perk_def.get("description", ""),
                        "icon": perk_def.get("icon", None),
                    }

        # 🔹 Enrichir les setItems directement
        if "setItems" in set_info:
            enriched_items = []
            for item_hash in set_info["setItems"]:
                item_hash_str = str(item_hash)
                if item_hash_str in item_data:
                    item_def = item_data[item_hash_str].get("displayProperties", {})
                    enriched_items.append({
                        "hash": item_hash,
                        "name": item_def.get("name", ""),
                        "icon": item_def.get("icon", None),
                    })
            # ⚡ Remplace directement setItems par la version enrichie
            set_info["setItems"] = enriched_items

    return data


# Enrichir les données
enriched_data = enrich_setarmor(setarmor_data)

# Sauvegarder
with open(enriched_file, "w", encoding="utf-8") as f:
    json.dump(enriched_data, f, ensure_ascii=False, indent=2)

print(f"✅ Enrichissement terminé. Résultat dans {enriched_file}")
