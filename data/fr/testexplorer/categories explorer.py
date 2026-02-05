#!/usr/bin/env python3
"""
Destiny 2 Item Category Explorer - Version Interactive v3
Génère une page HTML pour gérer les exclusions de catégories et items.
"""

import json
import os
from collections import defaultdict

# =============================================================================
# CONFIGURATION
# =============================================================================

DEFINITIONS = {
    "items": "../item_definitions.json",
    "categories": "../item_category_definitions.json",
}

EXCLUSIONS_CONFIG = "exclusions_config.json"
OUTPUT_HTML = "destiny_manager.html"


# =============================================================================
# FONCTIONS
# =============================================================================

def load_definition(name, path):
    if not os.path.exists(path):
        print(f"   ⚠️  {name}: non trouvé ({path})")
        return {}
    size_mb = os.path.getsize(path) / (1024 * 1024)
    print(f"   ✓ {name}: {path} ({size_mb:.1f} MB)")
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def load_all_definitions():
    print("📂 Chargement des définitions...")
    data = {}
    for key, path in DEFINITIONS.items():
        data[key] = load_definition(key, path)
    if not data.get("items"):
        print("\n❌ DestinyInventoryItemDefinition requis!")
        raise FileNotFoundError()
    return data


def load_exclusions():
    if os.path.exists(EXCLUSIONS_CONFIG):
        print(f"📋 Chargement des exclusions: {EXCLUSIONS_CONFIG}")
        with open(EXCLUSIONS_CONFIG, "r", encoding="utf-8") as f:
            return json.load(f)
    return {"excludedCategories": [], "excludedPlugCategories": [], "excludedItems": []}


def analyze_items(definitions, exclusions):
    print("\n🔍 Analyse des items...")
    items = definitions.get("items", {})
    categories_def = definitions.get("categories", {})

    excluded_cats = set(exclusions.get("excludedCategories", []))
    excluded_plugs = set(exclusions.get("excludedPlugCategories", []))
    excluded_items = set(exclusions.get("excludedItems", []))

    data = {
        "categories": {},
        "items_by_category": defaultdict(list),
        "items_by_plug_category": defaultdict(list),
        "plug_categories": set(),
        "plug_category_hashes": {},
        "all_items": {},
        "stats": {"total": 0, "excluded": 0}
    }

    # Indexe toutes les catégories
    for hash_str, cat in categories_def.items():
        data["categories"][hash_str] = {
            "hash": int(hash_str),
            "name": cat.get("displayProperties", {}).get("name", "Sans nom"),
            "description": cat.get("displayProperties", {}).get("description", ""),
            "visible": cat.get("visible", True),
            "deprecated": cat.get("deprecated", False),
        }

    total = len(items)
    for idx, (hash_str, item) in enumerate(items.items()):
        if idx % 10000 == 0:
            print(f"   {idx:,}/{total:,}...")

        if item.get("redacted") or item.get("blacklisted"):
            continue

        item_hash = item.get("hash")

        if item_hash in excluded_items:
            data["stats"]["excluded"] += 1
            continue

        item_cats = item.get("itemCategoryHashes", [])
        remaining_cats = [str(c) for c in item_cats if str(c) not in excluded_cats]

        plug = item.get("plug")
        plug_cat_id = plug.get("plugCategoryIdentifier", "") if plug else ""

        if plug_cat_id and plug_cat_id in excluded_plugs:
            data["stats"]["excluded"] += 1
            continue

        data["stats"]["total"] += 1

        item_info = {
            "hash": item_hash,
            "name": item.get("displayProperties", {}).get("name", "???"),
            "icon": item.get("displayProperties", {}).get("icon", ""),
            "itemType": item.get("itemType", 0),
            "itemTypeName": item.get("itemTypeDisplayName", ""),
            "tierName": item.get("itemTypeAndTierDisplayName", ""),
            "categoryHashes": [str(c) for c in item_cats],
        }

        data["all_items"][item_hash] = item_info

        if plug:
            plug_cat_hash = plug.get("plugCategoryHash")
            item_info["plugCategoryId"] = plug_cat_id
            if plug_cat_id:
                data["plug_categories"].add(plug_cat_id)
                data["items_by_plug_category"][plug_cat_id].append(item_info)
                if plug_cat_hash:
                    data["plug_category_hashes"][plug_cat_id] = plug_cat_hash

        for cat_hash in remaining_cats:
            data["items_by_category"][cat_hash].append(item_info)

    return data


def generate_html(data, exclusions):
    print("\n🎨 Génération du HTML...")

    categories_json = {}
    for h, c in data["categories"].items():
        categories_json[h] = {
            "hash": c["hash"],
            "name": c["name"],
            "description": c["description"],
            "visible": c["visible"],
            "deprecated": c["deprecated"],
            "items": [
                {
                    "hash": i["hash"],
                    "name": i["name"],
                    "icon": i["icon"],
                    "typeName": i["itemTypeName"],
                    "categoryHashes": i["categoryHashes"]
                }
                for i in data["items_by_category"].get(h, [])
            ]
        }

    plug_cats_json = {}
    for pc in sorted(data["plug_categories"]):
        plug_cats_json[pc] = {
            "id": pc,
            "hash": data["plug_category_hashes"].get(pc),
            "items": [
                {
                    "hash": i["hash"],
                    "name": i["name"],
                    "icon": i["icon"],
                    "typeName": i.get("itemTypeName", ""),
                    "categoryHashes": i["categoryHashes"]
                }
                for i in data["items_by_plug_category"].get(pc, [])
            ]
        }

    html = f'''<!DOCTYPE html>
<html lang="fr">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Destiny 2 - Gestionnaire d'exclusions</title>
    <style>
        :root {{
            --bg: #0d1117;
            --bg2: #161b22;
            --bg3: #21262d;
            --bg4: #30363d;
            --text: #c9d1d9;
            --text2: #8b949e;
            --accent: #58a6ff;
            --red: #f85149;
            --green: #3fb950;
            --orange: #d29922;
            --border: #30363d;
        }}

        * {{
            box-sizing: border-box;
            margin: 0;
            padding: 0;
        }}

        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
            background: var(--bg);
            color: var(--text);
        }}

        .layout {{
            display: flex;
            height: 100vh;
        }}

        /* ============ SIDEBAR ============ */
        .sidebar {{
            width: 350px;
            background: var(--bg2);
            border-right: 1px solid var(--border);
            display: flex;
            flex-direction: column;
            flex-shrink: 0;
        }}

        .sidebar-header {{
            padding: 15px;
            border-bottom: 1px solid var(--border);
        }}

        .sidebar-header h1 {{
            font-size: 1.2em;
            color: var(--accent);
            margin-bottom: 5px;
        }}

        .sidebar-controls {{
            display: flex;
            gap: 8px;
            margin-top: 10px;
        }}

        .sidebar-controls label {{
            display: flex;
            align-items: center;
            gap: 5px;
            font-size: 0.8em;
            color: var(--text2);
            cursor: pointer;
        }}

        .sidebar-tabs {{
            display: flex;
            border-bottom: 1px solid var(--border);
        }}

        .sidebar-tab {{
            flex: 1;
            padding: 10px;
            background: none;
            border: none;
            color: var(--text2);
            cursor: pointer;
            font-size: 0.85em;
        }}

        .sidebar-tab:hover {{
            background: var(--bg3);
        }}

        .sidebar-tab.active {{
            background: var(--bg3);
            color: var(--accent);
            border-bottom: 2px solid var(--accent);
        }}

        .sidebar-search {{
            padding: 10px;
            border-bottom: 1px solid var(--border);
        }}

        .sidebar-search input {{
            width: 100%;
            padding: 8px 12px;
            background: var(--bg);
            border: 1px solid var(--border);
            border-radius: 6px;
            color: var(--text);
        }}

        .sidebar-search input:focus {{
            outline: none;
            border-color: var(--accent);
        }}

        .sidebar-list {{
            flex: 1;
            overflow-y: auto;
        }}

        /* ============ LIST ITEMS ============ */
        .list-item {{
            display: flex;
            align-items: center;
            padding: 10px 15px;
            border-bottom: 1px solid var(--border);
            cursor: pointer;
            gap: 10px;
        }}

        .list-item:hover {{
            background: var(--bg3);
        }}

        .list-item.active {{
            background: var(--bg4);
            border-left: 3px solid var(--accent);
        }}

        .list-item.excluded {{
            opacity: 0.4;
            text-decoration: line-through;
            background: rgba(248,81,73,0.1);
        }}

        .list-item-info {{
            flex: 1;
            min-width: 0;
        }}

        .list-item-name {{
            font-size: 0.9em;
            white-space: nowrap;
            overflow: hidden;
            text-overflow: ellipsis;
        }}

        .list-item-meta {{
            font-size: 0.75em;
            color: var(--text2);
        }}

        .list-item-count {{
            font-size: 0.75em;
            background: var(--bg4);
            padding: 2px 8px;
            border-radius: 10px;
        }}

        .list-item-exclude {{
            background: none;
            border: none;
            color: var(--text2);
            cursor: pointer;
            padding: 5px;
            font-size: 1.1em;
        }}

        .list-item-exclude:hover {{
            color: var(--red);
        }}

        .list-item.excluded .list-item-exclude {{
            color: var(--green);
        }}

        /* ============ MAIN CONTENT ============ */
        .main {{
            flex: 1;
            display: flex;
            flex-direction: column;
            overflow: hidden;
        }}

        .main-header {{
            padding: 20px;
            border-bottom: 1px solid var(--border);
            background: var(--bg2);
        }}

        .main-header h2 {{
            font-size: 1.3em;
            margin-bottom: 5px;
        }}

        .main-header p {{
            color: var(--text2);
            font-size: 0.9em;
        }}

        .main-actions {{
            display: flex;
            gap: 10px;
            margin-top: 15px;
            flex-wrap: wrap;
        }}

        .btn {{
            padding: 8px 16px;
            border-radius: 6px;
            border: 1px solid var(--border);
            background: var(--bg3);
            color: var(--text);
            cursor: pointer;
            font-size: 0.85em;
        }}

        .btn:hover {{
            background: var(--bg4);
        }}

        .btn.primary {{
            background: var(--accent);
            color: #000;
            border-color: var(--accent);
        }}

        .btn.danger {{
            background: var(--red);
            color: #fff;
            border-color: var(--red);
        }}

        /* ============ FILTERS ============ */
        .filters-section {{
            margin-top: 15px;
            padding-top: 15px;
            border-top: 1px solid var(--border);
        }}

        .filters-section h4 {{
            font-size: 0.85em;
            color: var(--text2);
            margin-bottom: 10px;
        }}

        .filters-container {{
            display: flex;
            flex-wrap: wrap;
            gap: 6px;
            max-height: 120px;
            overflow-y: auto;
            padding: 5px;
            background: var(--bg);
            border-radius: 6px;
        }}

        .filter-tag {{
            font-size: 0.75em;
            padding: 4px 8px;
            border-radius: 4px;
            background: var(--accent);
            color: #000;
            cursor: pointer;
            transition: all 0.15s;
            display: flex;
            align-items: center;
            gap: 4px;
        }}

        .filter-tag:hover {{
            opacity: 0.8;
        }}

        .filter-tag.unchecked {{
            background: var(--bg4);
            color: var(--text2);
            opacity: 0.6;
        }}

        .filter-tag .filter-count {{
            font-size: 0.9em;
            opacity: 0.7;
        }}

        .filters-actions {{
            margin-top: 8px;
            display: flex;
            gap: 8px;
            align-items: center;
        }}

        .filters-actions button {{
            font-size: 0.75em;
            padding: 4px 8px;
        }}

        .main-content {{
            flex: 1;
            overflow-y: auto;
            padding: 20px;
        }}

        /* ============ ITEMS GRID ============ */
        .items-header {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 15px;
        }}

        .items-header h3 {{
            color: var(--text2);
            font-size: 0.9em;
        }}

        .items-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(320px, 1fr));
            gap: 10px;
        }}

        /* ============ ITEM CARDS ============ */
        .item-card {{
            display: flex;
            flex-direction: column;
            padding: 12px;
            background: var(--bg2);
            border: 1px solid var(--border);
            border-radius: 6px;
        }}

        .item-card:hover {{
            border-color: var(--accent);
        }}

        .item-card.excluded {{
            opacity: 0.35;
            background: rgba(248,81,73,0.05);
        }}

        .item-card.excluded .item-name {{
            text-decoration: line-through;
        }}

        .item-card.hidden {{
            display: none;
        }}

        .item-main {{
            display: flex;
            align-items: center;
            gap: 10px;
        }}

        .item-icon {{
            width: 44px;
            height: 44px;
            border-radius: 4px;
            background: var(--bg);
            flex-shrink: 0;
        }}

        .item-info {{
            flex: 1;
            min-width: 0;
        }}

        .item-name {{
            font-size: 0.9em;
            white-space: nowrap;
            overflow: hidden;
            text-overflow: ellipsis;
        }}

        .item-type {{
            font-size: 0.75em;
            color: var(--text2);
        }}

        .item-hash {{
            font-family: monospace;
            font-size: 0.7em;
            color: var(--accent);
        }}

        .item-exclude {{
            background: none;
            border: none;
            color: var(--text2);
            cursor: pointer;
            padding: 8px;
            font-size: 1em;
        }}

        .item-exclude:hover {{
            color: var(--red);
        }}

        .item-card.excluded .item-exclude {{
            color: var(--green);
        }}

        /* ============ ITEM CATEGORIES ============ */
        .item-categories {{
            display: flex;
            flex-wrap: wrap;
            gap: 4px;
            margin-top: 8px;
            padding-top: 8px;
            border-top: 1px solid var(--border);
        }}

        .item-cat-tag {{
            font-size: 0.7em;
            padding: 2px 6px;
            border-radius: 4px;
            background: var(--bg4);
            color: var(--text2);
            white-space: nowrap;
        }}

        .item-cat-tag.clickable {{
            cursor: pointer;
            transition: all 0.15s;
        }}

        .item-cat-tag.clickable:hover {{
            background: var(--accent);
            color: #000;
        }}

        .item-cat-tag.excluded {{
            opacity: 0.4;
            text-decoration: line-through;
            background: rgba(248,81,73,0.2);
        }}

        .item-cat-tag.current {{
            background: var(--accent);
            color: #000;
        }}

        /* ============ CONFIG PANEL ============ */
        .config-panel {{
            position: fixed;
            top: 0;
            right: -450px;
            width: 450px;
            height: 100vh;
            background: var(--bg2);
            border-left: 1px solid var(--border);
            transition: right 0.3s;
            z-index: 100;
            display: flex;
            flex-direction: column;
        }}

        .config-panel.open {{
            right: 0;
        }}

        .config-header {{
            padding: 20px;
            border-bottom: 1px solid var(--border);
            display: flex;
            justify-content: space-between;
            align-items: center;
        }}

        .config-header h2 {{
            font-size: 1.1em;
        }}

        .config-close {{
            background: none;
            border: none;
            color: var(--text);
            font-size: 1.5em;
            cursor: pointer;
        }}

        .config-content {{
            flex: 1;
            overflow-y: auto;
            padding: 20px;
        }}

        .config-content textarea {{
            width: 100%;
            height: 300px;
            background: var(--bg);
            border: 1px solid var(--border);
            border-radius: 6px;
            color: var(--text);
            font-family: monospace;
            font-size: 0.8em;
            padding: 15px;
            resize: vertical;
        }}

        .config-content h3 {{
            margin: 20px 0 10px;
            font-size: 0.9em;
            color: var(--text2);
        }}

        .config-stats {{
            background: var(--bg3);
            padding: 15px;
            border-radius: 6px;
            margin-bottom: 20px;
        }}

        .config-stats p {{
            margin: 5px 0;
            font-size: 0.9em;
        }}

        .config-stats span {{
            color: var(--accent);
            font-weight: 600;
        }}

        .config-actions {{
            padding: 20px;
            border-top: 1px solid var(--border);
            display: flex;
            gap: 10px;
        }}

        /* ============ OVERLAY & MISC ============ */
        .overlay {{
            position: fixed;
            top: 0;
            left: 0;
            right: 0;
            bottom: 0;
            background: rgba(0,0,0,0.5);
            z-index: 99;
            display: none;
        }}

        .overlay.open {{
            display: block;
        }}

        .welcome {{
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
            height: 100%;
            color: var(--text2);
            text-align: center;
            padding: 40px;
        }}

        .welcome h2 {{
            color: var(--text);
            margin-bottom: 10px;
        }}

        .badge {{
            font-size: 0.7em;
            padding: 2px 6px;
            border-radius: 4px;
            margin-left: 5px;
        }}

        .badge.deprecated {{
            background: var(--red);
            color: #fff;
        }}

        .badge.hidden {{
            background: var(--orange);
            color: #000;
        }}
    </style>
</head>
<body>

<div class="layout">
    <!-- Sidebar -->
    <div class="sidebar">
        <div class="sidebar-header">
            <h1>🎮 Destiny Manager</h1>
            <p style="font-size:0.8em;color:var(--text2)">{data["stats"]["total"]:,} items</p>
            <div class="sidebar-controls">
                <label>
                    <input type="checkbox" id="hide-excluded" onchange="toggleHideExcluded()">
                    Masquer les exclus
                </label>
            </div>
        </div>
        <div class="sidebar-tabs">
            <button class="sidebar-tab active" onclick="switchTab('categories')">Categories</button>
            <button class="sidebar-tab" onclick="switchTab('plugs')">Plug Types</button>
        </div>
        <div class="sidebar-search">
            <input type="text" id="search" placeholder="🔍 Rechercher..." oninput="filterList()">
        </div>
        <div class="sidebar-list" id="sidebar-list"></div>
    </div>

    <!-- Main -->
    <div class="main">
        <div class="main-header" id="main-header" style="display:none">
            <h2 id="selected-name">-</h2>
            <p id="selected-desc">-</p>
            <div class="main-actions">
                <button class="btn" onclick="toggleAllItems(true)">✓ Tout inclure</button>
                <button class="btn" onclick="toggleAllItems(false)">✗ Tout exclure</button>
                <button class="btn primary" onclick="openConfig()">💾 Config (<span id="exclusion-count">0</span>)</button>
            </div>
            <div class="filters-section" id="filters-section" style="display:none">
                <h4>🏷️ Filtrer par catégories (décocher = masquer les items ayant cette catégorie)</h4>
                <div class="filters-container" id="filters-container"></div>
                <div class="filters-actions">
                    <button class="btn" onclick="clearDisplayFilters()">Tout cocher</button>
                    <span id="filtered-count" style="font-size:0.8em;color:var(--text2);margin-left:10px;"></span>
                </div>
            </div>
        </div>
        <div class="main-content" id="main-content">
            <div class="welcome">
                <h2>👈 Sélectionne une catégorie</h2>
                <p>Clique sur une catégorie pour voir et gérer ses items</p>
            </div>
        </div>
    </div>
</div>

<!-- Config Panel -->
<div class="overlay" id="overlay" onclick="closeConfig()"></div>
<div class="config-panel" id="config-panel">
    <div class="config-header">
        <h2>💾 Configuration d'exclusions</h2>
        <button class="config-close" onclick="closeConfig()">×</button>
    </div>
    <div class="config-content">
        <div class="config-stats">
            <p>Catégories exclues: <span id="stat-cats">0</span></p>
            <p>Plug categories exclues: <span id="stat-plugs">0</span></p>
            <p>Items individuels exclus: <span id="stat-items">0</span></p>
        </div>
        <h3>JSON à copier dans exclusions_config.json :</h3>
        <textarea id="config-json" readonly></textarea>
    </div>
    <div class="config-actions">
        <button class="btn primary" onclick="copyConfig()">📋 Copier</button>
        <button class="btn" onclick="downloadConfig()">⬇️ Télécharger</button>
        <button class="btn danger" onclick="resetConfig()">🗑️ Reset</button>
    </div>
</div>

<script>
// =============================================================================
// DATA
// =============================================================================
const categories = {json.dumps(categories_json, ensure_ascii=False)};
const plugCategories = {json.dumps(plug_cats_json, ensure_ascii=False)};

// =============================================================================
// STATE
// =============================================================================
let currentTab = 'categories';
let selectedId = null;
let exclusions = {json.dumps(exclusions, ensure_ascii=False)};
let hideExcluded = false;
let displayFilters = new Set(); // Catégories DÉCOCHÉES (items avec ces cats seront masqués)

// =============================================================================
// INIT
// =============================================================================
document.addEventListener('DOMContentLoaded', () => {{
    renderList();
    updateConfigStats();
}});

// =============================================================================
// SIDEBAR
// =============================================================================
function toggleHideExcluded() {{
    hideExcluded = document.getElementById('hide-excluded').checked;
    renderList();
    if (selectedId) {{
        applyDisplayFilters();
    }}
}}

function switchTab(tab) {{
    currentTab = tab;
    selectedId = null;
    displayFilters.clear();

    document.querySelectorAll('.sidebar-tab').forEach(t => t.classList.remove('active'));
    const tabIndex = tab === 'categories' ? 'first' : 'last';
    document.querySelector(`.sidebar-tab:${{tabIndex}}-child`).classList.add('active');

    document.getElementById('search').value = '';
    document.getElementById('main-header').style.display = 'none';
    document.getElementById('main-content').innerHTML = `
        <div class="welcome">
            <h2>👈 Sélectionne une catégorie</h2>
            <p>Clique sur une catégorie pour voir et gérer ses items</p>
        </div>`;

    renderList();
}}

function filterList() {{
    renderList();
}}

function renderList() {{
    const list = document.getElementById('sidebar-list');
    const search = document.getElementById('search').value.toLowerCase();
    let html = '';

    if (currentTab === 'categories') {{
        const sorted = Object.entries(categories).sort((a, b) => a[1].name.localeCompare(b[1].name));

        for (const [hash, cat] of sorted) {{
            if (search && !cat.name.toLowerCase().includes(search) && !hash.includes(search)) continue;

            const excluded = exclusions.excludedCategories.includes(hash);
            if (hideExcluded && excluded) continue;

            const badges = (cat.deprecated ? '<span class="badge deprecated">obsolète</span>' : '') +
                          (!cat.visible ? '<span class="badge hidden">caché</span>' : '');

            html += `
                <div class="list-item ${{excluded ? 'excluded' : ''}} ${{selectedId === hash ? 'active' : ''}}" 
                     onclick="selectCategory('${{hash}}')" data-id="${{hash}}">
                    <div class="list-item-info">
                        <div class="list-item-name">${{cat.name || '(sans nom)'}}${{badges}}</div>
                        <div class="list-item-meta">${{hash}}</div>
                    </div>
                    <span class="list-item-count">${{cat.items.length}}</span>
                    <button class="list-item-exclude" onclick="event.stopPropagation();toggleCategory('${{hash}}')" 
                            title="${{excluded ? 'Inclure' : 'Exclure'}}">
                        ${{excluded ? '↩️' : '🚫'}}
                    </button>
                </div>`;
        }}
    }} else {{
        const sorted = Object.entries(plugCategories).sort((a, b) => a[0].localeCompare(b[0]));

        for (const [id, pc] of sorted) {{
            if (search && !id.toLowerCase().includes(search)) continue;

            const excluded = exclusions.excludedPlugCategories.includes(id);
            if (hideExcluded && excluded) continue;

            html += `
                <div class="list-item ${{excluded ? 'excluded' : ''}} ${{selectedId === id ? 'active' : ''}}" 
                     onclick="selectPlugCategory('${{id}}')" data-id="${{id}}">
                    <div class="list-item-info">
                        <div class="list-item-name">${{id}}</div>
                        <div class="list-item-meta">hash: ${{pc.hash || '?'}}</div>
                    </div>
                    <span class="list-item-count">${{pc.items.length}}</span>
                    <button class="list-item-exclude" onclick="event.stopPropagation();togglePlugCategory('${{id}}')" 
                            title="${{excluded ? 'Inclure' : 'Exclure'}}">
                        ${{excluded ? '↩️' : '🚫'}}
                    </button>
                </div>`;
        }}
    }}

    list.innerHTML = html || '<p style="padding:20px;color:var(--text2)">Aucun résultat</p>';
}}

function scrollToSelectedInSidebar(id) {{
    setTimeout(() => {{
        const el = document.querySelector(`.list-item[data-id="${{id}}"]`);
        if (el) {{
            el.scrollIntoView({{ behavior: 'smooth', block: 'center' }});
        }}
    }}, 50);
}}

// =============================================================================
// SELECTION
// =============================================================================
function selectCategory(hash) {{
    selectedId = hash;
    currentTab = 'categories';
    displayFilters.clear();

    document.querySelectorAll('.sidebar-tab').forEach(t => t.classList.remove('active'));
    document.querySelector('.sidebar-tab:first-child').classList.add('active');

    const cat = categories[hash];
    document.getElementById('main-header').style.display = 'block';
    document.getElementById('selected-name').textContent = cat.name || '(sans nom)';
    document.getElementById('selected-desc').textContent = cat.description || 'Aucune description';

    renderItems(cat.items, 'category', hash);
    renderFilters(cat.items);
    renderList();
    scrollToSelectedInSidebar(hash);
}}

function selectPlugCategory(id) {{
    selectedId = id;
    currentTab = 'plugs';
    displayFilters.clear();

    document.querySelectorAll('.sidebar-tab').forEach(t => t.classList.remove('active'));
    document.querySelector('.sidebar-tab:last-child').classList.add('active');

    const pc = plugCategories[id];
    document.getElementById('main-header').style.display = 'block';
    document.getElementById('selected-name').textContent = id;
    document.getElementById('selected-desc').textContent = `${{pc.items.length}} items • hash: ${{pc.hash || '?'}}`;

    renderItems(pc.items, 'plug', id);
    renderFilters(pc.items);
    renderList();
    scrollToSelectedInSidebar(id);
}}

// =============================================================================
// HELPERS
// =============================================================================
function getCategoryName(hash) {{
    return categories[hash]?.name || hash;
}}

function isCategoryExcluded(hash) {{
    return exclusions.excludedCategories.includes(hash);
}}

// =============================================================================
// FILTERS
// =============================================================================
function renderFilters(items) {{
    const container = document.getElementById('filters-container');
    const section = document.getElementById('filters-section');

    // Compte les catégories présentes dans les items
    const catCounts = {{}};
    for (const item of items) {{
        for (const catHash of item.categoryHashes || []) {{
            catCounts[catHash] = (catCounts[catHash] || 0) + 1;
        }}
    }}

    const sortedCats = Object.entries(catCounts)
        .sort((a, b) => b[1] - a[1])
        .slice(0, 50);

    if (sortedCats.length === 0) {{
        section.style.display = 'none';
        return;
    }}

    section.style.display = 'block';
    let html = '';

    for (const [catHash, count] of sortedCats) {{
        const name = getCategoryName(catHash);
        const isUnchecked = displayFilters.has(catHash);

        html += `
            <span class="filter-tag ${{isUnchecked ? 'unchecked' : ''}}" 
                  onclick="toggleDisplayFilter('${{catHash}}')"
                  data-hash="${{catHash}}"
                  title="${{isUnchecked ? 'Cocher: afficher ces items' : 'Décocher: masquer les items avec cette catégorie'}}">
                ${{name}} <span class="filter-count">(${{count}})</span>
            </span>`;
    }}

    container.innerHTML = html;
    updateFilteredCount();
}}

function toggleDisplayFilter(catHash) {{
    if (displayFilters.has(catHash)) {{
        displayFilters.delete(catHash);
    }} else {{
        displayFilters.add(catHash);
    }}

    applyDisplayFilters();

    document.querySelectorAll('.filter-tag').forEach(tag => {{
        const hash = tag.dataset.hash;
        tag.classList.toggle('unchecked', displayFilters.has(hash));
    }});

    updateFilteredCount();
}}

function clearDisplayFilters() {{
    displayFilters.clear();
    applyDisplayFilters();
    document.querySelectorAll('.filter-tag').forEach(tag => tag.classList.remove('unchecked'));
    updateFilteredCount();
}}

function applyDisplayFilters() {{
    const cards = document.querySelectorAll('.item-card');
    let visibleCount = 0;
    let totalCount = cards.length;

    cards.forEach(card => {{
        const isExcluded = card.classList.contains('excluded');
        const catHashes = card.dataset.categories ? card.dataset.categories.split(',') : [];
        const hasFilteredCat = catHashes.some(h => displayFilters.has(h));

        const shouldHide = (hideExcluded && isExcluded) || hasFilteredCat;
        card.classList.toggle('hidden', shouldHide);

        if (!shouldHide) visibleCount++;
    }});

    const headerText = (displayFilters.size > 0 || hideExcluded)
        ? `${{visibleCount}} / ${{totalCount}} items affichés`
        : `${{totalCount}} items`;

    document.querySelector('.items-header h3').textContent = headerText;
}}

function updateFilteredCount() {{
    const el = document.getElementById('filtered-count');
    el.textContent = displayFilters.size > 0 ? `${{displayFilters.size}} filtre(s) actif(s)` : '';
}}

// =============================================================================
// ITEMS
// =============================================================================
function renderItems(items, type, parentId) {{
    const container = document.getElementById('main-content');
    const excludedItems = exclusions.excludedItems;

    let html = `
        <div class="items-header">
            <h3>${{items.length}} items</h3>
        </div>
        <div class="items-grid">`;

    for (const item of items) {{
        const excluded = excludedItems.includes(item.hash);
        if (hideExcluded && excluded) continue;

        const iconUrl = item.icon ? 'https://www.bungie.net' + item.icon : '';
        const catHashesStr = (item.categoryHashes || []).join(',');

        // Génère les tags de catégories
        let catTagsHtml = '';
        if (item.categoryHashes && item.categoryHashes.length > 0) {{
            catTagsHtml = '<div class="item-categories">';

            for (const catHash of item.categoryHashes) {{
                const catName = getCategoryName(catHash);
                const isExcluded = isCategoryExcluded(catHash);
                const isCurrentCat = catHash === parentId;

                if (isExcluded) {{
                    catTagsHtml += `<span class="item-cat-tag excluded" title="Catégorie exclue">${{catName}}</span>`;
                }} else if (isCurrentCat) {{
                    catTagsHtml += `<span class="item-cat-tag current">${{catName}}</span>`;
                }} else {{
                    catTagsHtml += `<span class="item-cat-tag clickable" onclick="event.stopPropagation();selectCategory('${{catHash}}')" title="Voir cette catégorie">${{catName}}</span>`;
                }}
            }}

            catTagsHtml += '</div>';
        }}

        html += `
            <div class="item-card ${{excluded ? 'excluded' : ''}}" data-hash="${{item.hash}}" data-categories="${{catHashesStr}}">
                <div class="item-main">
                    ${{iconUrl ? `<img src="${{iconUrl}}" class="item-icon" loading="lazy" onerror="this.style.visibility='hidden'">` : '<div class="item-icon"></div>'}}
                    <div class="item-info">
                        <div class="item-name">${{item.name}}</div>
                        <div class="item-type">${{item.typeName || ''}}</div>
                        <div class="item-hash">${{item.hash}}</div>
                    </div>
                    <button class="item-exclude" onclick="toggleItem(${{item.hash}})" title="${{excluded ? 'Inclure' : 'Exclure'}}">
                        ${{excluded ? '↩️' : '🚫'}}
                    </button>
                </div>
                ${{catTagsHtml}}
            </div>`;
    }}

    html += '</div>';
    container.innerHTML = html;
}}

// =============================================================================
// EXCLUSIONS
// =============================================================================
function toggleCategory(hash) {{
    const idx = exclusions.excludedCategories.indexOf(hash);
    const cat = categories[hash];

    if (idx > -1) {{
        // Ré-inclure la catégorie (sans ré-inclure les items)
        exclusions.excludedCategories.splice(idx, 1);
    }} else {{
        // Exclure la catégorie ET tous ses items
        exclusions.excludedCategories.push(hash);
        if (cat && cat.items) {{
            for (const item of cat.items) {{
                if (!exclusions.excludedItems.includes(item.hash)) {{
                    exclusions.excludedItems.push(item.hash);
                }}
            }}
        }}
    }}

    renderList();

    if (selectedId && currentTab === 'categories') {{
        const c = categories[selectedId];
        if (c) {{
            renderItems(c.items, 'category', selectedId);
            renderFilters(c.items);
        }}
    }}

    updateConfigStats();
}}

function togglePlugCategory(id) {{
    const idx = exclusions.excludedPlugCategories.indexOf(id);
    const pc = plugCategories[id];

    if (idx > -1) {{
        // Ré-inclure le plug category (sans ré-inclure les items)
        exclusions.excludedPlugCategories.splice(idx, 1);
    }} else {{
        // Exclure le plug category ET tous ses items
        exclusions.excludedPlugCategories.push(id);
        if (pc && pc.items) {{
            for (const item of pc.items) {{
                if (!exclusions.excludedItems.includes(item.hash)) {{
                    exclusions.excludedItems.push(item.hash);
                }}
            }}
        }}
    }}

    renderList();

    if (selectedId && currentTab === 'plugs') {{
        const p = plugCategories[selectedId];
        if (p) {{
            renderItems(p.items, 'plug', selectedId);
            renderFilters(p.items);
        }}
    }}

    updateConfigStats();
}}

function toggleItem(hash) {{
    const idx = exclusions.excludedItems.indexOf(hash);
    if (idx > -1) {{
        exclusions.excludedItems.splice(idx, 1);
    }} else {{
        exclusions.excludedItems.push(hash);
    }}

    const card = document.querySelector(`.item-card[data-hash="${{hash}}"]`);
    if (card) {{
        const nowExcluded = exclusions.excludedItems.includes(hash);
        card.classList.toggle('excluded', nowExcluded);

        if (hideExcluded && nowExcluded) {{
            card.classList.add('hidden');
        }}

        const btn = card.querySelector('.item-exclude');
        btn.innerHTML = nowExcluded ? '↩️' : '🚫';
    }}

    updateConfigStats();
}}

function toggleAllItems(include) {{
    if (!selectedId) return;

    let items;
    if (currentTab === 'categories') {{
        items = categories[selectedId]?.items || [];
    }} else {{
        items = plugCategories[selectedId]?.items || [];
    }}

    // N'agit que sur les items visibles
    const visibleItems = items.filter(item => {{
        if (hideExcluded && exclusions.excludedItems.includes(item.hash)) {{
            return false;
        }}
        const hasFilteredCat = (item.categoryHashes || []).some(h => displayFilters.has(h));
        return !hasFilteredCat;
    }});

    for (const item of visibleItems) {{
        const idx = exclusions.excludedItems.indexOf(item.hash);
        if (include && idx > -1) {{
            exclusions.excludedItems.splice(idx, 1);
        }} else if (!include && idx === -1) {{
            exclusions.excludedItems.push(item.hash);
        }}
    }}

    if (currentTab === 'categories') {{
        selectCategory(selectedId);
    }} else {{
        selectPlugCategory(selectedId);
    }}

    updateConfigStats();
}}

// =============================================================================
// CONFIG
// =============================================================================
function updateConfigStats() {{
    document.getElementById('stat-cats').textContent = exclusions.excludedCategories.length;
    document.getElementById('stat-plugs').textContent = exclusions.excludedPlugCategories.length;
    document.getElementById('stat-items').textContent = exclusions.excludedItems.length;
    document.getElementById('config-json').value = JSON.stringify(exclusions, null, 2);

    const total = exclusions.excludedCategories.length + 
                  exclusions.excludedPlugCategories.length + 
                  exclusions.excludedItems.length;
    document.getElementById('exclusion-count').textContent = total;
}}

function openConfig() {{
    document.getElementById('overlay').classList.add('open');
    document.getElementById('config-panel').classList.add('open');
    updateConfigStats();
}}

function closeConfig() {{
    document.getElementById('overlay').classList.remove('open');
    document.getElementById('config-panel').classList.remove('open');
}}

function copyConfig() {{
    navigator.clipboard.writeText(document.getElementById('config-json').value);
    alert('Config copiée !');
}}

function downloadConfig() {{
    const blob = new Blob([document.getElementById('config-json').value], {{ type: 'application/json' }});
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = 'exclusions_config.json';
    a.click();
    URL.revokeObjectURL(url);
}}

function resetConfig() {{
    if (confirm('Supprimer toutes les exclusions ?')) {{
        exclusions = {{
            excludedCategories: [],
            excludedPlugCategories: [],
            excludedItems: []
        }};

        renderList();

        if (selectedId) {{
            if (currentTab === 'categories') {{
                selectCategory(selectedId);
            }} else {{
                selectPlugCategory(selectedId);
            }}
        }}

        updateConfigStats();
    }}
}}
</script>
</body>
</html>'''

    return html


def main():
    print("=" * 60)
    print("🚀 Destiny 2 Category Manager v3")
    print("=" * 60)

    definitions = load_all_definitions()
    exclusions = load_exclusions()
    data = analyze_items(definitions, exclusions)

    print(f"\n📊 Stats:")
    print(f"   - Items affichés: {data['stats']['total']:,}")
    print(f"   - Items exclus: {data['stats']['excluded']:,}")
    print(f"   - Catégories: {len(data['categories'])}")
    print(f"   - Plug categories: {len(data['plug_categories'])}")

    html = generate_html(data, exclusions)

    with open(OUTPUT_HTML, "w", encoding="utf-8") as f:
        f.write(html)

    print(f"\n✅ Généré: {OUTPUT_HTML}")


if __name__ == "__main__":
    main()