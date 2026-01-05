import json
import os

# Répertoires
data_dir = "../../../data"

# Fichiers source
setarmor_file = os.path.join(data_dir, "setarmor_definitions.json")
sandboxperk_file = os.path.join(data_dir, "sandboxperk_definitions.json")
item_file = os.path.join(data_dir, "item_definitions.json")
artefact_file = os.path.join(data_dir, "artefact_definitions.json")

# Fichiers de sortie
enriched_setarmor_file = os.path.join(data_dir, "setarmor_definitions_enriched.json")
enriched_artefact_file = os.path.join(data_dir, "artefact_definitions_enriched.json")

# Charger les JSON
with open(setarmor_file, "r", encoding="utf-8") as f:
    setarmor_data = json.load(f)

with open(sandboxperk_file, "r", encoding="utf-8") as f:
    sandboxperk_data = json.load(f)

with open(item_file, "r", encoding="utf-8") as f:
    item_data = json.load(f)

with open(artefact_file, "r", encoding="utf-8") as f:
    artefact_data = json.load(f)


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


def enrich_artefact(data):
    for artefact_id, artefact_info in data.items():

        # 🔹 Enrichir les items de chaque tier
        if "tiers" in artefact_info:
            for tier in artefact_info["tiers"]:
                if "items" in tier:
                    enriched_items = []
                    for item in tier["items"]:
                        item_hash = item["itemHash"]
                        item_hash_str = str(item_hash)

                        # 🔍 Étape 1 : Chercher l'item dans DestinyInventoryItemDefinition
                        if item_hash_str in item_data:
                            item_def = item_data[item_hash_str]

                            # 🔍 Étape 2 : Chercher les perks dans l'item
                            if "perks" in item_def:
                                for perk in item_def["perks"]:
                                    perk_hash = str(perk.get("perkHash", ""))

                                    # 🔍 Étape 3 : Chercher le perk dans DestinySandboxPerkDefinition
                                    if perk_hash in sandboxperk_data:
                                        perk_def = sandboxperk_data[perk_hash].get("displayProperties", {})

                                        # ✅ On a trouvé une correspondance, on enrichit
                                        enriched_items.append({
                                            "itemHash": item_hash,
                                            "perkHash": perk_hash,
                                            "name": perk_def.get("name", ""),
                                            "description": perk_def.get("description", ""),
                                            "icon": perk_def.get("icon", None),
                                        })
                                        # On ne prend que le premier perk trouvé
                                        break
                                else:
                                    # Aucun perk trouvé dans sandboxperk_data
                                    enriched_items.append({
                                        "itemHash": item_hash,
                                        "perkHash": None,
                                        "name": "",
                                        "description": "",
                                        "icon": None,
                                    })
                            else:
                                # Pas de perks dans l'item
                                enriched_items.append({
                                    "itemHash": item_hash,
                                    "perkHash": None,
                                    "name": "",
                                    "description": "",
                                    "icon": None,
                                })
                        else:
                            # Item non trouvé dans item_data
                            enriched_items.append({
                                "itemHash": item_hash,
                                "perkHash": None,
                                "name": "",
                                "description": "",
                                "icon": None,
                            })

                    # ⚡ Remplace directement items par la version enrichie
                    tier["items"] = enriched_items

    return data


# Enrichir les données
enriched_setarmor = enrich_setarmor(setarmor_data)
enriched_artefact = enrich_artefact(artefact_data)

# Sauvegarder
with open(enriched_setarmor_file, "w", encoding="utf-8") as f:
    json.dump(enriched_setarmor, f, ensure_ascii=False)

with open(enriched_artefact_file, "w", encoding="utf-8") as f:
    json.dump(enriched_artefact, f, ensure_ascii=False)

print(f"✅ Enrichissement terminé.")
print(f"   - SetArmor: {enriched_setarmor_file}")
print(f"   - Artefact: {enriched_artefact_file}")