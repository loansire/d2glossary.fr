import pandas as pd
import re
import json

SHEET_ID = "1tfa3mEwTWLrPUEw2p9aRKWUH37quVgpkyVisB6E1DZU"

sheets = {
    "WeaponPerks": "1703329297",
    "SeasonWeaponPerks": "296976005",
    "WeaponMods": "296976005",
    "IntrinsicTraits": "1368736324",
    "OriginTraits": "1050893845",
    "ArmorSets": "1916736284",
}

# Configuration des styles
styles_config = {
    # Pattern ↑ : Ligne complète enhanced (commence par ↑)
    "enhanced_line": {
        "pattern": r'^(â†\'[^\n]+)$',
        "class": "enhanced-line",
        "flags": re.MULTILINE
    },

    # Pattern ↑ : Valeur â†' Valeur (ex: +10 â†'+12, 15% â†'20%, 0.8x â†'0.75x)
    "upgrade_value": {
        "pattern": r'([\+\-]?\d+\.?\d*[%x]?)\s*(â†\')\s*([\+\-]?\d+\.?\d*[%x]?\??)',
        "replacement": r'<span class="base-value">\1</span><span class="upgrade-arrow">\2</span><span class="enhanced-value">\3</span>',
        "class": None  # Remplacement custom
    },

    # Pattern ↑ : Ajout (â†'and +X, â†'or +X)
    "enhanced_addition": {
        "pattern": r'(â†\')(and |or )([^,\.\n]+)',
        "replacement": r'<span class="upgrade-arrow">\1</span><span class="enhanced-addition">\2\3</span>',
        "class": None
    },

    # Pattern ↑ : Texte enhanced restant
    "enhanced_text": {
        "pattern": r'(â†\')([^â†\'\n]+?)(?=\.|,|\n|â†\'|$)',
        "replacement": r'<span class="upgrade-arrow">\1</span><span class="enhanced-text">\2</span>',
        "class": None
    },

    # Valeurs incertaines (avec ?)
    "uncertain": {
        "pattern": r'(\d+\.?\d*[%x]?\?|\?\d*%?|\[\?\]|\?%)',
        "class": "uncertain"
    },

    # Stats positives (+X)
    "stat_positive": {
        "pattern": r'(\+\d+\.?\d*%?)',
        "class": "stat-positive"
    },

    # Stats négatives (-X)
    "stat_negative": {
        "pattern": r'(-\d+\.?\d*%?)',
        "class": "stat-negative"
    },

    # Durées (X seconds)
    "duration": {
        "pattern": r'(\d+\.?\d*\s*seconds?)',
        "class": "duration"
    },

    # Multiplicateurs (0.Xx, X.Xx)
    "multiplier": {
        "pattern": r'(\d+\.?\d*x)\b',
        "class": "multiplier"
    },

    # Noms de stats
    "stats": {
        "pattern": r'\b(Range|Stability|Handling|Reload Speed|Reload|Aim Assist|Blast Radius|Velocity|Magazine|Charge Rate|Draw Time|Guard Resistance|Guard Efficiency|Guard Endurance|Airborne Effectiveness|Recoil Direction|Zoom|Flinch Resist|Accuracy|Impact|Ammo Generation|Mobility|Recovery|Resilience|Precision Damage|Precision Hit|Precision Kill|Weapon Kill|Weapon Damage)\b',
        "class": "stat"
    },

    # Solar Verbs
    "solar": {
        "pattern": r'\b(Scorch|Scorched|Scorching|Ignition|Ignite|Ignites|Cure|Restoration|Radiant|Firesprite|Firesprites)\b',
        "class": "solar"
    },

    # Arc Verbs
    "arc": {
        "pattern": r'\b(Jolt|Jolted|Jolting|Blind|Blinded|Amplified|Speed Booster|Ionic Trace|Ionic Traces|Bolt Charge)\b',
        "class": "arc"
    },

    # Void Verbs
    "void": {
        "pattern": r'\b(Suppress|Suppression|Suppressed|Weaken|Weakened|Volatile|Void Overshield|Devour|Invisibility|Invisible|Void Breach|Void Breaches)\b',
        "class": "void"
    },

    # Stasis Verbs
    "stasis": {
        "pattern": r'\b(Slow|Slowed|Freeze|Frozen|Shatter|Shattered|Stasis Crystal|Stasis Crystals|Stasis Shard|Stasis Shards|Frost Armor)\b',
        "class": "stasis"
    },

    # Strand Verbs
    "strand": {
        "pattern": r'\b(Sever|Severed|Suspend|Suspended|Unravel|Unraveling|Woven Mail|Tangle|Tangles|Threadling|Threadlings)\b',
        "class": "strand"
    },

    # Éléments
    "elements": {
        "pattern": r'\b(Solar|Arc|Void|Stasis|Strand|Kinetic)\b',
        "class": "element"
    },

    # Types d'armes
    "weapon_types": {
        "pattern": r'\b(Auto Rifles?|Scout Rifles?|Pulse Rifles?|Hand Cannons?|Sidearms?|Submachine Guns?|Shotguns?|Sniper Rifles?|Fusion Rifles?|Linear Fusion Rifles?|Trace Rifles?|Grenade Launchers?|Rocket Launchers?|Swords?|Glaives?|Bows?|Machine Guns?|Primary Weapons?|Special Weapons?|Power Weapons?|Heavy Weapons?|Energy Weapons?)\b',
        "class": "weapon-type"
    },

    # Frames
    "frames": {
        "pattern": r'\b(Adaptive Frame|Aggressive Frame|Precision Frame|Rapid-Fire Frame|High-Impact Frame|Lightweight Frame|Heavy Burst|Support Frame|Area Denial Frame|Wave Frame|Adaptive Burst)\b',
        "class": "frame"
    },

    # Champions
    "champions": {
        "pattern": r'\b(Champions?|Barrier Champions?|Overload Champions?|Unstoppable Champions?|Barrier Champion\'?s? Shield|Stunning a Champion)\b',
        "class": "champion"
    },

    # Types d'ennemis
    "enemy_ranks": {
        "pattern": r'\b(Rank-and-File|Rank-And-File|Elites?|Miniboss|Minibosses|Boss|Bosses|Guardians?|Combatants?|Vehicles?|Constructs?|Turrets?)\b',
        "class": "enemy-rank"
    },

    # Capacités
    "abilities": {
        "pattern": r'\b(Grenade Ability|Melee Ability|Class Ability|Super Ability|Powered Melee|Finisher|Grenade Kill|Melee Kill|Super|Transcendence|Transcending|Orb of Power|Orbs of Power)\b',
        "class": "ability"
    },

    # Conditions de déclenchement
    "triggers": {
        "pattern": r'\b(On Weapon Kill|On Precision Kill|On Precision Hit|On Hit|On Melee Kill|On Ally Death|On Ally Revival|Upon finishing a reload|Upon readying|Upon sliding|Upon sprinting|Upon picking up|Upon scoring|Upon dealing|Upon breaking|Upon reaching|Upon blocking|While ADS|While Crouched|While Airborne|While Guarding|While within|While no enemies|While no allies|While at Full|While at Critical|After sprinting|After having maintained)\b',
        "class": "trigger"
    },

    # Stacks
    "stacks": {
        "pattern": r'\b(x\d+|up to a maximum of \d+ stacks?|\d+ stacks?|per stack)\b',
        "class": "stack"
    },

    # Munitions / Pickups
    "ammo_pickups": {
        "pattern": r'\b(Ammo Bricks?|Primary Ammo|Special Ammo|Heavy Ammo|Reserves|Ammo Generation)\b',
        "class": "ammo"
    },

    # États du joueur
    "player_states": {
        "pattern": r'\b(Critical Health|Overshield|Shield HP|ADS|Hipfire|Hipfiring|Last Guardian Standing|Full Magazine|Magazine Capacity)\b',
        "class": "player-state"
    },

    # Dégâts spéciaux
    "damage_types": {
        "pattern": r'\b(Explosive Damage|Impact Damage|Precision Damage|Elemental Damage|Kinetic Damage|Bodyshot Damage|Weakspot|Direct Hit|Direct Hits)\b',
        "class": "damage-type"
    },

    # Boucliers
    "shields": {
        "pattern": r'\b(Elemental Shields?|Matching Shields?|Non-Matching Shields?|Guardian Shields?|Combatant Shields?)\b',
        "class": "shield"
    }
}

# CSS correspondant
css_styles = """
:root {
    --color-base-value: #74c0fc;
    --color-upgrade-arrow: #51cf66;
    --color-enhanced-value: #51cf66;
    --color-enhanced-line: #51cf66;
    --color-enhanced-addition: #8ce99a;
    --color-enhanced-text: #51cf66;
    --color-uncertain: #fcc419;
    --color-stat-positive: #339af0;
    --color-stat-negative: #ff6b6b;
    --color-duration: #fcc419;
    --color-multiplier: #20c997;
    --color-stat: #74c0fc;
    --color-solar: #ff6b35;
    --color-arc: #7ec8e3;
    --color-void: #b388ff;
    --color-stasis: #4fc3f7;
    --color-strand: #66bb6a;
    --color-element: #f06595;
    --color-weapon-type: #adb5bd;
    --color-frame: #868e96;
    --color-champion: #ffd43b;
    --color-enemy-rank: #ffe066;
    --color-ability: #da77f2;
    --color-trigger: #ced4da;
    --color-stack: #e599f7;
    --color-ammo: #69db7c;
    --color-player-state: #ffa94d;
    --color-damage-type: #ff8787;
    --color-shield: #fab005;
}

.base-value { color: var(--color-base-value); }
.upgrade-arrow { color: var(--color-upgrade-arrow); font-weight: bold; }
.enhanced-value { color: var(--color-enhanced-value); font-weight: bold; }
.enhanced-line { 
    color: var(--color-enhanced-line); 
    font-style: italic; 
    display: block; 
    border-left: 3px solid var(--color-enhanced-line); 
    padding-left: 8px; 
    margin-top: 4px; 
}
.enhanced-addition { color: var(--color-enhanced-addition); }
.enhanced-text { color: var(--color-enhanced-text); }
.uncertain { color: var(--color-uncertain); font-style: italic; }
.stat-positive { color: var(--color-stat-positive); }
.stat-negative { color: var(--color-stat-negative); }
.duration { color: var(--color-duration); }
.multiplier { color: var(--color-multiplier); }
.stat { color: var(--color-stat); }
.solar { color: var(--color-solar); font-weight: 500; }
.arc { color: var(--color-arc); font-weight: 500; }
.void { color: var(--color-void); font-weight: 500; }
.stasis { color: var(--color-stasis); font-weight: 500; }
.strand { color: var(--color-strand); font-weight: 500; }
.element { color: var(--color-element); }
.weapon-type { color: var(--color-weapon-type); }
.frame { color: var(--color-frame); }
.champion { color: var(--color-champion); font-weight: bold; }
.enemy-rank { color: var(--color-enemy-rank); }
.ability { color: var(--color-ability); }
.trigger { color: var(--color-trigger); font-style: italic; }
.stack { color: var(--color-stack); }
.ammo { color: var(--color-ammo); }
.player-state { color: var(--color-player-state); }
.damage-type { color: var(--color-damage-type); }
.shield { color: var(--color-shield); }
"""


def stylize_text(text):
    """Applique les styles au texte"""
    if not isinstance(text, str):
        return text

    # Ordre d'application important : patterns ↑ en premier
    priority_order = [
        "enhanced_line",
        "upgrade_value",
        "enhanced_addition",
        "enhanced_text",
        "uncertain",
        "multiplier",
        "duration",
        "stat_positive",
        "stat_negative",
        "stats",
        "solar",
        "arc",
        "void",
        "stasis",
        "strand",
        "elements",
        "weapon_types",
        "frames",
        "champions",
        "enemy_ranks",
        "abilities",
        "triggers",
        "stacks",
        "ammo_pickups",
        "player_states",
        "damage_types",
        "shields"
    ]

    for style_name in priority_order:
        config = styles_config[style_name]
        pattern = config["pattern"]
        flags = config.get("flags", 0)

        if "replacement" in config:
            # Remplacement custom
            text = re.sub(pattern, config["replacement"], text, flags=flags)
        elif config.get("class"):
            # Remplacement standard avec classe
            css_class = config["class"]
            text = re.sub(
                pattern,
                rf'<span class="{css_class}">\1</span>',
                text,
                flags=flags
            )

    return text


def fetch_and_process_sheets():
    """Récupère et traite toutes les sheets"""
    all_data = {}

    for name, gid in sheets.items():
        print(f"📥 Récupération de {name}...")
        url = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/export?format=csv&gid={gid}"

        try:
            df = pd.read_csv(url)

            # Version brute (CSV)
            df_csv = df.copy()
            for col in df_csv.columns:
                if df_csv[col].dtype == 'object':
                    df_csv[col] = df_csv[col].str.replace('\r\n', '\\n', regex=False)
                    df_csv[col] = df_csv[col].str.replace('\n', '\\n', regex=False)
                    df_csv[col] = df_csv[col].str.replace('\r', '\\n', regex=False)
            df_csv.to_csv(f"data/{name}.csv", sep=";", index=False)

            # Version JSON brute
            df.to_json(f"data/{name}.json", orient="records", force_ascii=False, indent=2)

            # Version stylisée (HTML dans JSON)
            df_styled = df.copy()
            for col in df_styled.columns:
                if df_styled[col].dtype == 'object':
                    df_styled[col] = df_styled[col].apply(stylize_text)

            # Convertir en liste de dicts pour JSON
            records = df_styled.to_dict(orient="records")
            all_data[name] = records

            # Sauvegarder JSON stylisé individuel
            with open(f"data/{name}_styled.json", "w", encoding="utf-8") as f:
                json.dump(records, f, ensure_ascii=False, indent=2)

            print(f"✓ {name} exporté (CSV + JSON + JSON stylisé)")

        except Exception as e:
            print(f"✗ Erreur pour {name}: {e}")

    # Sauvegarder tout en un fichier
    with open("data/all_data_styled.json", "w", encoding="utf-8") as f:
        json.dump(all_data, f, ensure_ascii=False, indent=2)

    # Sauvegarder le CSS
    with open("data/styles.css", "w", encoding="utf-8") as f:
        f.write(css_styles)

    print("\n✓ CSS sauvegardé dans data/styles.css")
    print("✓ Données complètes sauvegardées dans data/all_data_styled.json")

    return all_data


def generate_html_preview(data, output_file="data/preview.html"):
    """Génère une page HTML complète"""
    html = f"""<!DOCTYPE html>
<html lang="fr">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>D2 Glossary</title>
    <style>
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background-color: #1a1a2e;
            color: #eee;
            padding: 20px;
            line-height: 1.6;
        }}
        h1 {{ color: #fff; border-bottom: 2px solid #51cf66; padding-bottom: 10px; }}
        h2 {{ color: #74c0fc; margin-top: 40px; }}
        .nav {{
            position: sticky;
            top: 0;
            background: #1a1a2e;
            padding: 10px 0;
            border-bottom: 1px solid #333;
            margin-bottom: 20px;
            z-index: 100;
        }}
        .nav a {{
            color: #74c0fc;
            margin-right: 15px;
            text-decoration: none;
        }}
        .nav a:hover {{
            color: #51cf66;
            text-decoration: underline;
        }}
        .perk {{
            background: #16213e;
            border-radius: 8px;
            padding: 15px;
            margin: 10px 0;
            border-left: 4px solid #51cf66;
        }}
        .perk-name {{
            font-size: 1.2em;
            font-weight: bold;
            color: #fff;
            margin-bottom: 8px;
        }}
        .perk-description {{
            white-space: pre-wrap;
        }}
        .count {{
            color: #868e96;
            font-size: 0.9em;
            margin-left: 10px;
        }}
        {css_styles}
    </style>
</head>
<body>
    <h1>🎮 Destiny 2 Glossary</h1>

    <nav class="nav">
"""

    # Navigation
    for sheet_name in data.keys():
        html += f'        <a href="#{sheet_name}">{sheet_name}</a>\n'

    html += "    </nav>\n"

    # Contenu complet
    for sheet_name, records in data.items():
        html += f'    <h2 id="{sheet_name}">{sheet_name}<span class="count">({len(records)} items)</span></h2>\n'

        for record in records:  # Plus de limite
            name = record.get("Name", "")
            description = record.get("Description", "")

            if name or description:
                html += f"""    <div class="perk">
        <div class="perk-name">{name if name else "—"}</div>
        <div class="perk-description">{description if description else "—"}</div>
    </div>
"""

    html += """
</body>
</html>
"""

    with open(output_file, "w", encoding="utf-8") as f:
        f.write(html)

    print(f"✓ HTML complet généré: {output_file}")


if __name__ == "__main__":
    import os

    os.makedirs("data", exist_ok=True)

    print("🚀 Démarrage de l'export D2 Glossary\n")
    data = fetch_and_process_sheets()
    generate_html_preview(data)
    print("\n✅ Export terminé!")