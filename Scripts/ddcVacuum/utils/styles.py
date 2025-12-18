import re

STYLES_CONFIG = {
    # === PATTERNS ↑ (priorité haute) ===
    "enhanced_line": {
        "pattern": r'^(â†\'[^\n]+)$',
        "class": "enhanced-line",
        "flags": re.MULTILINE
    },
    "upgrade_value": {
        "pattern": r'([\+\-]?\d+\.?\d*[%x]?)\s*(â†\')\s*([\+\-]?\d+\.?\d*[%x]?\??)',
        "replacement": r'<span class="base-value">\1</span><span class="upgrade-arrow">\2</span><span class="enhanced-value">\3</span>',
    },
    "enhanced_addition": {
        "pattern": r'(â†\')(and |or )([^,\.\n]+)',
        "replacement": r'<span class="upgrade-arrow">\1</span><span class="enhanced-addition">\2\3</span>',
    },
    "enhanced_text": {
        "pattern": r'(â†\')([^â†\'\n]+?)(?=\.|,|\n|â†\'|$)',
        "replacement": r'<span class="upgrade-arrow">\1</span><span class="enhanced-text">\2</span>',
    },

    # === VALEURS ===
    "uncertain": {
        "pattern": r'(\d+\.?\d*[%x]?\?|\?\d*%?|\[\?\]|\?%)',
        "class": "uncertain"
    },
    "stat_positive": {
        "pattern": r'(\+\d+\.?\d*%?)',
        "class": "stat-positive"
    },
    "stat_negative": {
        "pattern": r'(-\d+\.?\d*%?)',
        "class": "stat-negative"
    },
    "duration": {
        "pattern": r'(\d+\.?\d*\s*seconds?)',
        "class": "duration"
    },
    "multiplier": {
        "pattern": r'(\d+\.?\d*x)\b',
        "class": "multiplier"
    },

    # === STATS ===
    "stats": {
        "pattern": r'\b(Range|Stability|Handling|Reload Speed|Reload|Aim Assist|Blast Radius|Velocity|Magazine|Charge Rate|Draw Time|Guard Resistance|Guard Efficiency|Guard Endurance|Airborne Effectiveness|Recoil Direction|Zoom|Flinch Resist|Accuracy|Impact|Ammo Generation|Mobility|Recovery|Resilience|Precision Damage|Precision Hit|Precision Kill|Weapon Kill|Weapon Damage)\b',
        "class": "stat"
    },

    # === SUBCLASS VERBS ===
    "solar": {
        "pattern": r'\b(Scorch|Scorched|Scorching|Ignition|Ignite|Ignites|Cure|Restoration|Radiant|Firesprite|Firesprites)\b',
        "class": "solar"
    },
    "arc": {
        "pattern": r'\b(Jolt|Jolted|Jolting|Blind|Blinded|Amplified|Speed Booster|Ionic Trace|Ionic Traces|Bolt Charge)\b',
        "class": "arc"
    },
    "void": {
        "pattern": r'\b(Suppress|Suppression|Suppressed|Weaken|Weakened|Volatile|Void Overshield|Devour|Invisibility|Invisible|Void Breach|Void Breaches)\b',
        "class": "void"
    },
    "stasis": {
        "pattern": r'\b(Slow|Slowed|Freeze|Frozen|Shatter|Shattered|Stasis Crystal|Stasis Crystals|Stasis Shard|Stasis Shards|Frost Armor)\b',
        "class": "stasis"
    },
    "strand": {
        "pattern": r'\b(Sever|Severed|Suspend|Suspended|Unravel|Unraveling|Woven Mail|Tangle|Tangles|Threadling|Threadlings)\b',
        "class": "strand"
    },

    # === ÉLÉMENTS ===
    "elements": {
        "pattern": r'\b(Solar|Arc|Void|Stasis|Strand|Kinetic)\b',
        "class": "element"
    },

    # === ARMES ===
    "weapon_types": {
        "pattern": r'\b(Auto Rifles?|Scout Rifles?|Pulse Rifles?|Hand Cannons?|Sidearms?|Submachine Guns?|Shotguns?|Sniper Rifles?|Fusion Rifles?|Linear Fusion Rifles?|Trace Rifles?|Grenade Launchers?|Rocket Launchers?|Swords?|Glaives?|Bows?|Machine Guns?|Primary Weapons?|Special Weapons?|Power Weapons?|Heavy Weapons?|Energy Weapons?)\b',
        "class": "weapon-type"
    },
    "frames": {
        "pattern": r'\b(Adaptive Frame|Aggressive Frame|Precision Frame|Rapid-Fire Frame|High-Impact Frame|Lightweight Frame|Heavy Burst|Support Frame|Area Denial Frame|Wave Frame|Adaptive Burst)\b',
        "class": "frame"
    },

    # === ENNEMIS ===
    "champions": {
        "pattern": r'\b(Champions?|Barrier Champions?|Overload Champions?|Unstoppable Champions?|Barrier Champion\'?s? Shield|Stunning a Champion)\b',
        "class": "champion"
    },
    "enemy_ranks": {
        "pattern": r'\b(Rank-and-File|Rank-And-File|Elites?|Miniboss|Minibosses|Boss|Bosses|Guardians?|Combatants?|Vehicles?|Constructs?|Turrets?)\b',
        "class": "enemy-rank"
    },

    # === GAMEPLAY ===
    "abilities": {
        "pattern": r'\b(Grenade Ability|Melee Ability|Class Ability|Super Ability|Powered Melee|Finisher|Grenade Kill|Melee Kill|Super|Transcendence|Transcending|Orb of Power|Orbs of Power)\b',
        "class": "ability"
    },
    "triggers": {
        "pattern": r'\b(On Weapon Kill|On Precision Kill|On Precision Hit|On Hit|On Melee Kill|On Ally Death|On Ally Revival|Upon finishing a reload|Upon readying|Upon sliding|Upon sprinting|Upon picking up|Upon scoring|Upon dealing|Upon breaking|Upon reaching|Upon blocking|While ADS|While Crouched|While Airborne|While Guarding|While within|While no enemies|While no allies|While at Full|While at Critical|After sprinting|After having maintained)\b',
        "class": "trigger"
    },
    "stacks": {
        "pattern": r'\b(x\d+|up to a maximum of \d+ stacks?|\d+ stacks?|per stack)\b',
        "class": "stack"
    },
    "ammo_pickups": {
        "pattern": r'\b(Ammo Bricks?|Primary Ammo|Special Ammo|Heavy Ammo|Reserves|Ammo Generation)\b',
        "class": "ammo"
    },
    "player_states": {
        "pattern": r'\b(Critical Health|Overshield|Shield HP|ADS|Hipfire|Hipfiring|Last Guardian Standing|Full Magazine|Magazine Capacity)\b',
        "class": "player-state"
    },
    "damage_types": {
        "pattern": r'\b(Explosive Damage|Impact Damage|Precision Damage|Elemental Damage|Kinetic Damage|Bodyshot Damage|Weakspot|Direct Hit|Direct Hits)\b',
        "class": "damage-type"
    },
    "shields": {
        "pattern": r'\b(Elemental Shields?|Matching Shields?|Non-Matching Shields?|Guardian Shields?|Combatant Shields?)\b',
        "class": "shield"
    }
}

# Ordre d'application des styles
STYLES_ORDER = [
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

CSS_STYLES = """
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