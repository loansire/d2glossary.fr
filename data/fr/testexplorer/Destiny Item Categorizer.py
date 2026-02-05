# destiny_item_categorizer.py
import json
from collections import defaultdict

# === FICHIERS ===
ITEM_DEFINITIONS_FILE = "../item_definitions.json"
ITEM_CATEGORY_DEFINITION_FILE = "../item_category_definitions.json"
OUTPUT_FILE = "destiny-items-preview.html"

# === ARCHÉTYPES D'ARMES ===
WEAPON_ARCHETYPES = [
    "Revolvers",
    "Fusils à impulsion",
    "Fusils automatiques",
    "Fusils à pompe",
    "Lance-grenades",
    "Fusils à fusion",
    "Fusils d'éclaireur",
    "Pistolets-mitrailleurs",
    "Fusils de précision",
    "Pistolets",
    "Lance-roquettes",
    "Épées",
    "Arcs",
    "Mitrailleuses",
    "Fusils à fusion linéaire",
    "Fusils à rayon",
    "Glaives",
]

# === PRIORITÉ DES TIERS ===
TIER_PRIORITY = {
    "exotic": 0,
    "legendary": 1,
    "rare": 2,
    "uncommon": 3,
    "common": 4,
    "unknown": 5,
}


def load_json(filepath: str) -> dict:
    print(f"📖 Chargement de {filepath}...")
    with open(filepath, "r", encoding="utf-8") as f:
        return json.load(f)


def build_category_map(item_categories: dict) -> dict[int, str]:
    return {
        int(hash_): cat.get("displayProperties", {}).get("name", "Inconnu")
        for hash_, cat in item_categories.items()
    }


def get_tier_from_traits(trait_ids: list) -> str:
    """Détermine le tier via traitIds."""
    if "item.weapon.exotic" in trait_ids or "item.armor.exotic" in trait_ids:
        return "exotic"
    # Par défaut legendary (le manifest n'a pas les autres tiers)
    return "legendary"


def categorize_item(item: dict, category_map: dict[int, str]) -> tuple[str, str] | None:
    """Retourne (catégorie, sous-catégorie) ou None."""
    cats = item.get("itemCategoryHashes") or []
    cat_names = [category_map.get(h, "") for h in cats]
    cat_names_lower = [c.lower() for c in cat_names]
    joined = " | ".join(cat_names_lower)

    trait_ids = item.get("traitIds") or []

    # Exclure les engrams
    if "item.engram" in trait_ids:
        return None

    item_type = item.get("itemType")

    # === ARMES (itemType=3) ===
    if item_type == 3 and "armes" in cat_names_lower:
        # Trouver l'archétype
        archetype = "Autre"
        for arch in WEAPON_ARCHETYPES:
            if arch in cat_names:
                archetype = arch
                break
        return ("weapons", archetype)

    # === ARMURES (itemType=2) ===
    if item_type == 2 and "armures" in cat_names_lower:
        if "item.armor.exotic" in trait_ids:
            return ("armors_exotic", None)
        else:
            return ("armors_legendary", None)

    # === MODS/PERKS (itemType=19) ===
    if item_type == 19:
        # Particularités d'origine
        if "particularités d'origine" in joined:
            return ("origin_traits", None)

        # Perks traits (Armature = Libellule, Boucherie, etc.)
        if "mods d'arme : armature" in joined:
            return ("weapon_perks_traits", None)

        # Perks colonnes 1-2 (fusionnés)
        if "mods d'arme : chargeurs" in joined:
            return ("weapon_perks_columns", "Chargeurs")
        if "mods d'arme : canons" in joined:
            return ("weapon_perks_columns", "Canons")
        if "mods d'arme : batteries" in joined:
            return ("weapon_perks_columns", "Batteries")
        if "mods d'arme : lunettes" in joined or "mods d'arme : viseurs" in joined:
            return ("weapon_perks_columns", "Optiques")
        if "mods d'arme : poignées" in joined:
            return ("weapon_perks_columns", "Poignées")
        if "mods d'arme : tubes de lancement" in joined:
            return ("weapon_perks_columns", "Tubes")
        if "flèches" in joined:
            return ("weapon_perks_columns", "Flèches")
        if "manches" in joined:
            return ("weapon_perks_columns", "Manches")

        # Intrinsèques
        if "mods d'arme : intrinsèque" in joined:
            name = (item.get("displayProperties") or {}).get("name", "").lower()
            if any(kw in name for kw in ["chasseur", "titan", "arcaniste", "hunter", "warlock"]):
                return ("armor_intrinsics", None)
            else:
                return ("weapon_intrinsics", None)

        # Mods d'armure par slot
        if "mods d'armure : casque" in joined:
            return ("armor_mods", "Casque")
        if "mods d'armure : gantelets" in joined:
            return ("armor_mods", "Gantelets")
        if "mods d'armure : armure de torse" in joined:
            return ("armor_mods", "Torse")
        if "mods d'armure : armure de jambes" in joined:
            return ("armor_mods", "Jambes")
        if "mods d'armure : objet de classe" in joined:
            return ("armor_mods", "Classe")

        # Mods d'armure généraux
        if "mods d'armure" in cat_names_lower and not any("ornements" in c for c in cat_names_lower):
            return ("armor_mods", "Général")

    return None


def generate_html(categorized_items: dict, stats: dict) -> str:
    category_names = {
        "weapons": "⚔️ Armes",
        "armors_exotic": "🔶 Armures Exotiques",
        "armors_legendary": "💜 Armures Légendaires",
        "origin_traits": "🏷️ Particularités d'Origine",
        "weapon_intrinsics": "⚔️ Intrinsèques d'Armes",
        "armor_intrinsics": "🛡️ Intrinsèques d'Armures",
        "weapon_perks_traits": "🎯 Perks Armes - Traits",
        "weapon_perks_columns": "🔧 Perks Armes - Colonnes 1-2",
        "armor_mods": "👕 Mods d'Armure",
    }

    category_order = [
        "weapons",
        "armors_exotic", "armors_legendary",
        "origin_traits",
        "weapon_intrinsics", "armor_intrinsics",
        "weapon_perks_traits",
        "weapon_perks_columns",
        "armor_mods",
    ]

    # Catégories avec sous-colonnes
    multi_column_categories = ["weapons", "weapon_perks_columns", "armor_mods"]

    html = f"""<!DOCTYPE html>
<html lang="fr">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Destiny 2 Item Categorizer</title>
  <style>
    * {{ box-sizing: border-box; }}
    body {{
      font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
      background: #1a1a2e;
      color: #eee;
      margin: 0;
      padding: 20px;
    }}
    h1 {{ text-align: center; color: #f0c040; margin-bottom: 10px; }}
    .stats {{
      text-align: center;
      color: #888;
      margin-bottom: 30px;
      font-size: 14px;
    }}
    .stats span {{ 
      margin: 0 15px;
      padding: 5px 10px;
      background: #252540;
      border-radius: 4px;
    }}
    .category {{
      margin-bottom: 40px;
      background: #252540;
      border-radius: 8px;
      padding: 20px;
    }}
    .category-header {{
      display: flex;
      justify-content: space-between;
      align-items: center;
      margin-bottom: 15px;
      padding-bottom: 10px;
      border-bottom: 2px solid #f0c040;
    }}
    .category-header h2 {{ margin: 0; color: #f0c040; font-size: 1.3em; }}
    .category-count {{
      background: #f0c040;
      color: #1a1a2e;
      padding: 4px 12px;
      border-radius: 20px;
      font-weight: bold;
      font-size: 14px;
    }}
    .items-grid {{
      display: grid;
      grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
      gap: 10px;
      max-height: 400px;
      overflow-y: auto;
      padding-right: 10px;
    }}
    .items-grid::-webkit-scrollbar {{ width: 8px; }}
    .items-grid::-webkit-scrollbar-track {{ background: #1a1a2e; border-radius: 4px; }}
    .items-grid::-webkit-scrollbar-thumb {{ background: #f0c040; border-radius: 4px; }}

    /* Multi-column layout */
    .multi-columns {{
      display: flex;
      gap: 15px;
      flex-wrap: wrap;
    }}
    .sub-column {{
      flex: 1;
      min-width: 250px;
      max-width: 350px;
      background: #1a1a2e;
      border-radius: 6px;
      padding: 10px;
    }}
    .sub-column h3 {{
      margin: 0 0 10px 0;
      color: #888;
      font-size: 0.9em;
      border-bottom: 1px solid #3a3a5e;
      padding-bottom: 5px;
    }}
    .sub-column .items-list {{
      max-height: 350px;
      overflow-y: auto;
      padding-right: 5px;
    }}
    .sub-column .items-list::-webkit-scrollbar {{ width: 6px; }}
    .sub-column .items-list::-webkit-scrollbar-track {{ background: #252540; border-radius: 3px; }}
    .sub-column .items-list::-webkit-scrollbar-thumb {{ background: #f0c040; border-radius: 3px; }}

    .item {{
      display: flex;
      align-items: center;
      gap: 10px;
      background: #1a1a2e;
      padding: 8px;
      border-radius: 6px;
      transition: transform 0.1s, background 0.1s;
      margin-bottom: 5px;
    }}
    .multi-columns .item {{
      background: #252540;
    }}
    .item:hover {{ transform: translateY(-2px); background: #2a2a4e; }}
    .item img {{
      width: 48px;
      height: 48px;
      border-radius: 4px;
      background: #333;
      flex-shrink: 0;
    }}
    .item-info {{ overflow: hidden; }}
    .item-name {{
      font-size: 13px;
      font-weight: 500;
      white-space: nowrap;
      overflow: hidden;
      text-overflow: ellipsis;
    }}
    .item-hash {{ font-size: 10px; color: #666; font-family: monospace; }}
    .tier-exotic .item-name {{ color: #ceae32; }}
    .tier-legendary .item-name {{ color: #a855f7; }}
    .tier-rare .item-name {{ color: #5076a3; }}
    .tier-uncommon .item-name {{ color: #4ade80; }}
    .tier-common .item-name {{ color: #c3bcb4; }}
    .toggle-btn {{
      background: #3a3a5e;
      border: none;
      color: #eee;
      padding: 5px 15px;
      border-radius: 4px;
      cursor: pointer;
      font-size: 12px;
      margin-left: 10px;
    }}
    .toggle-btn:hover {{ background: #4a4a6e; }}
    .collapsed .items-grid, .collapsed .multi-columns {{ display: none; }}
    .search-box {{
      width: 100%;
      max-width: 400px;
      margin: 0 auto 30px;
      display: block;
      padding: 12px 20px;
      border: 2px solid #3a3a5e;
      border-radius: 25px;
      background: #252540;
      color: #eee;
      font-size: 16px;
    }}
    .search-box:focus {{ outline: none; border-color: #f0c040; }}
    .hidden {{ display: none !important; }}
  </style>
</head>
<body>
  <h1>🎮 Destiny 2 Item Categorizer</h1>
  <div class="stats">
    <span>Total: {stats['total']}</span>
    <span>Catégorisés: {stats['categorized']}</span>
    <span>Non catégorisés: {stats['uncategorized']}</span>
  </div>

  <input type="text" class="search-box" placeholder="🔍 Rechercher un item..." id="searchInput">

  <div id="categories">"""

    for cat_key in category_order:
        cat_data = categorized_items.get(cat_key, {})
        if not cat_data:
            continue

        cat_name = category_names.get(cat_key, cat_key)

        # Compter le total
        if isinstance(cat_data, dict):
            total_count = sum(len(items) for items in cat_data.values())
        else:
            total_count = len(cat_data)

        html += f"""
    <div class="category" data-category="{cat_key}">
      <div class="category-header">
        <h2>{cat_name}</h2>
        <div>
          <span class="category-count">{total_count}</span>
          <button class="toggle-btn" onclick="toggleCategory(this)">Réduire</button>
        </div>
      </div>"""

        if cat_key in multi_column_categories and isinstance(cat_data, dict):
            # Multi-column layout
            html += """
      <div class="multi-columns">"""

            # Pour les armes, trier par ordre des archétypes
            if cat_key == "weapons":
                sorted_keys = sorted(cat_data.keys(),
                                     key=lambda x: WEAPON_ARCHETYPES.index(x) if x in WEAPON_ARCHETYPES else 999)
            else:
                sorted_keys = sorted(cat_data.keys())

            for sub_cat in sorted_keys:
                items = cat_data[sub_cat]
                # Trier par tier (exotic > legendary > rare > etc) puis par nom
                items_sorted = sorted(items, key=lambda x: (
                TIER_PRIORITY.get(x.get("tier_name", "unknown"), 99), x.get("name", "")))

                html += f"""
        <div class="sub-column">
          <h3>{sub_cat} ({len(items)})</h3>
          <div class="items-list">"""

                for item in items_sorted:
                    tier_class = f"tier-{item.get('tier_name', 'unknown')}"
                    name = item.get("name", "Sans nom")
                    name_escaped = name.replace('"', '&quot;').replace('<', '&lt;')
                    html += f"""
            <div class="item {tier_class}" data-name="{name_escaped.lower()}">
              <img src="{item.get('icon', '')}" alt="" loading="lazy" onerror="this.style.display='none'">
              <div class="item-info">
                <div class="item-name" title="{name_escaped}">{name}</div>
                <div class="item-hash">{item.get('hash', '')}</div>
              </div>
            </div>"""

                html += """
          </div>
        </div>"""

            html += """
      </div>"""
        else:
            # Standard grid layout
            if isinstance(cat_data, dict):
                items_list = []
                for items in cat_data.values():
                    items_list.extend(items)
            else:
                items_list = cat_data

            items_sorted = sorted(items_list, key=lambda x: (
            TIER_PRIORITY.get(x.get("tier_name", "unknown"), 99), x.get("name", "")))

            html += """
      <div class="items-grid">"""

            for item in items_sorted:
                tier_class = f"tier-{item.get('tier_name', 'unknown')}"
                name = item.get("name", "Sans nom")
                name_escaped = name.replace('"', '&quot;').replace('<', '&lt;')
                html += f"""
        <div class="item {tier_class}" data-name="{name_escaped.lower()}">
          <img src="{item.get('icon', '')}" alt="" loading="lazy" onerror="this.style.display='none'">
          <div class="item-info">
            <div class="item-name" title="{name_escaped}">{name}</div>
            <div class="item-hash">{item.get('hash', '')}</div>
          </div>
        </div>"""

            html += """
      </div>"""

        html += """
    </div>"""

    html += """
  </div>

  <script>
    function toggleCategory(btn) {
      const category = btn.closest('.category');
      category.classList.toggle('collapsed');
      btn.textContent = category.classList.contains('collapsed') ? 'Développer' : 'Réduire';
    }

    document.getElementById('searchInput').addEventListener('input', function(e) {
      const search = e.target.value.toLowerCase().trim();
      document.querySelectorAll('.item').forEach(item => {
        const name = item.dataset.name;
        item.classList.toggle('hidden', search && !name.includes(search));
      });
    });
  </script>
</body>
</html>"""

    return html


def main():
    items = load_json(ITEM_DEFINITIONS_FILE)
    item_categories = load_json(ITEM_CATEGORY_DEFINITION_FILE)

    category_map = build_category_map(item_categories)

    print(f"\n📦 {len(items)} items trouvés")
    print(f"📂 {len(category_map)} catégories chargées")

    print("\n🏷️  Catégorisation en cours...")
    categorized_items = defaultdict(lambda: defaultdict(list))
    categorized_count = 0

    for item in items.values():
        result = categorize_item(item, category_map)

        if result:
            category, sub_category = result
            display_props = item.get("displayProperties") or {}
            icon = display_props.get("icon", "")
            if icon and not icon.startswith("http"):
                icon = f"https://www.bungie.net{icon}"

            trait_ids = item.get("traitIds") or []
            tier_name = get_tier_from_traits(trait_ids)

            item_data = {
                "hash": item.get("hash"),
                "name": display_props.get("name", ""),
                "icon": icon,
                "tier_name": tier_name,
            }

            if sub_category:
                categorized_items[category][sub_category].append(item_data)
            else:
                categorized_items[category]["_default"].append(item_data)

            categorized_count += 1

    # Convertir les catégories sans sous-cat en listes simples
    final_items = {}
    for cat, sub_cats in categorized_items.items():
        if list(sub_cats.keys()) == ["_default"]:
            final_items[cat] = sub_cats["_default"]
        else:
            final_items[cat] = dict(sub_cats)

    stats = {
        "total": len(items),
        "categorized": categorized_count,
        "uncategorized": len(items) - categorized_count,
    }

    print("\n📊 Statistiques:")
    for cat, data in sorted(final_items.items()):
        if isinstance(data, dict):
            total = sum(len(v) for v in data.values())
            print(f"   {cat}: {total}")
            for sub, items_list in sorted(data.items()):
                print(f"      - {sub}: {len(items_list)}")
        else:
            print(f"   {cat}: {len(data)}")

    print("\n🎨 Génération du HTML...")
    html = generate_html(final_items, stats)

    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        f.write(html)

    print(f"✅ Fichier généré: {OUTPUT_FILE}")


if __name__ == "__main__":
    main()