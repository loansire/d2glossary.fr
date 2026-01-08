"""
Style pattern definitions for DDCVacuum

Defines regex patterns and CSS classes for:
- Enhanced perks (arrows)
- PvE/PvP values
- Elements (Solar, Arc, Void, Stasis, Strand, Prismatic, Kinetic)
- Champions (Barrier, Overload, Unstoppable)
- Ammo types (Primary, Special, Heavy)
- Weapon types (Auto Rifle, Scout Rifle, etc.)
"""

# =============================================================================
# PATTERN DEFINITIONS - Order matters for application priority
# =============================================================================

STYLE_PATTERNS = {
    # === ENHANCED PERK INDICATORS ===
    "enhanced_arrow_text": {
        "pattern": r'(↑[a-zA-Z\s](?:(?!\.\s|\.$).)*\.)',
        "class": "enhancedArrow",
        "description": "Enhanced perk: arrow + letter/space then until period (included)"
    },
    "enhanced_arrow_value": {
        "pattern": r'(↑(?![a-zA-Z\s])\S+)',
        "class": "enhancedArrow",
        "description": "Enhanced perk: arrow + non-letter/space until first space"
    },

    # === PVE/PVP VALUES ===
    "pvp_value": {
        "pattern": r'\[([^\]]+)\]',
        "class": "pvp",
        "capture_group": 1,
        "description": "PVP-specific values in brackets"
    },

    # === ELEMENTS / SUBCLASSES ===
    "solar_keywords": {
        "pattern": r'\b(Well of Radiance|Blade Barrage|Song of Flame|Ember of \w+|Firesprites?|Restoration|Scorching|Ignitions?|Scorched|Daybreak|Golden Gun|Ignited|Ignites|Radiant|Scorch|Solar|Cure)\b',
        "class": "solar",
        "description": "Solar subclass keywords"
    },
    "arc_keywords": {
        "pattern": r'\b(Fist of Havoc|Speed Booster|Thundercrash|Ionic Traces?|Stormtrance|Bolt Charge|Arc Staff|Jolting Shot|Jolt Shot|Amplified|Blinded|Jolted|Blind|Jolt|Arc)\b',
        "class": "arc",
        "description": "Arc subclass keywords"
    },
    "void_keywords": {
        "pattern": r'\b(Chaos Accelerant|Void (?:Overshield|Breaches?)|Invisibility|Suppressions?|Suppressed|Echo of \w+|Smoke Bomb|Weakening|Invisible|Weakened|Volatile|Overshield|Devour|Weaken|Void)\b',
        "class": "void",
        "description": "Void subclass keywords"
    },
    "stasis_keywords": {
        "pattern": r'\b(Stasis (?:Crystals?|Seekers?|Shards?|Debuff)|Whisper of \w+|Glacial Guard|Frost Armor|Shattering|Shattered|Shatter|Slowed|Frozens?|Freeze|Stasis|Slow)\b',
        "class": "stasis",
        "description": "Stasis subclass keywords"
    },
    "strand_keywords": {
        "pattern": r'\b(Unraveling(?: Rounds)?|Thread of \w+|Threadlings?|Woven Mail|Unravel|Tangles?|Severed|Suspends?(?:ed)?|Strand|Sever)\b',
        "class": "strand",
        "description": "Strand subclass keywords"
    },
    "kinetic_keywords": {
        "pattern": r'\b(Kinetic(?: (?:Bonus |Weapon |Synthesis )?(?:Damage|Weapons?|Blasts?|Micro-Missile|Ammo))?)\b',
        "class": "kinetic",
        "description": "Kinetic subclass keywords"
    },
    "prismatic_keywords": {
        "pattern": r'\b(Transcend(?:ence|ing))\b',
        "class": "prismatic",
        "description": "Prismatic subclass keywords"
    },

    # === CHAMPIONS ===
    "barrier_champion": {
        "pattern": r'\bBarrier Champions?(?:\'s)?\b',
        "class": "barrier",
        "description": "Barrier champion references"
    },
    "overload_champion": {
        "pattern": r'\b(?:Overload Champions?(?:\'s)?|Disruption)\b',
        "class": "overload",
        "description": "Overload champion references"
    },
    "unstoppable_champion": {
        "pattern": r'\bUnstoppable Champions?(?:\'s)?\b',
        "class": "unstoppable",
        "description": "Unstoppable champion references"
    },

    # === AMMO TYPES ===
    "primary_ammo": {
        "pattern": r'\bPrimary (?:Ammo(?: (?:Reserves?|Weapons?|Bricks?))?|Weapons?)\b',
        "class": "primary",
        "description": "Primary ammo type"
    },
    "special_ammo": {
        "pattern": r'\bSpecial(?: (?:Ammo(?: (?:Reserves?|Weapons?|Bricks?))?|Weapons?))?\b',
        "class": "special",
        "description": "Special ammo type"
    },
    "heavy_ammo": {
        "pattern": r'\b(?:Heavy|Power) (?:(?:Ammo|Weapon)s?(?: (?:Reserves?|Bricks?))?|Bricks?)\b',
        "class": "heavy",
        "description": "Heavy/Power ammo type"
    },

    # === WEAPON TYPES ===
    "auto_rifle": {
        "pattern": r'\b(?:(?:High-Impact|Lightweight|Support|Adaptative|Rapid-Fire|Rocket|Non-Burst|\d{3}RPM(?: and \d{3}RPM)*) )?Auto(?:\s+Rifles?|(?=:))',
        "class": "weapon-auto-rifle",
        "description": "Auto Rifle weapon type"
    },
    "pulse_rifle": {
        "pattern": r'\b(?:(?:High-Impact|Lightweight|Adaptative|Rapid-Fire|Special|Rocket|Non-Burst|\d{3}RPM(?: and \d{3}RPM)*) )?Pulse(?: Rifles?)?\b',
        "class": "weapon-pulse-rifle",
        "description": "Pulse Rifle weapon type"
    },
    "scout_rifle": {
        "pattern": r'\b(?:(?:High-Impact|Lightweight|Adaptative|Rapid-Fire|Rocket|Non-Burst|\d{3}RPM(?: and \d{3}RPM)*) )?Scout Rifles?\b',
        "class": "weapon-scout-rifle",
        "description": "Scout Rifle weapon type"
    },
    "hand_cannon": {
        "pattern": r'\b(?:(?:High-Impact|Lightweight|Adaptative|Rapid-Fire|Rocket|Special|Non-Burst|\d{3}RPM(?: and \d{3}RPM)*) )?Hand Cannons?\b',
        "class": "weapon-hand-cannon",
        "description": "Hand Cannon weapon type"
    },
    "sidearm": {
        "pattern": r'\b(?:(?:High-Impact|Lightweight|Adaptative|Rapid-Fire|Special|Rocket|Non-Burst|\d{3}RPM(?: and \d{3}RPM)*) )?Sidearms?\b',
        "class": "weapon-sidearm",
        "description": "Sidearm weapon type"
    },
    "submachine_gun": {
        "pattern": r'\b(?:(?:(?:High-Impact|Lightweight|Adaptative|Rapid-Fire|Rocket|Non-Burst|\d{3}RPM(?: and \d{3}RPM)*) )?Submachine Guns?|SMGs?)\b',
        "class": "weapon-smg",
        "description": "Submachine Gun weapon type"
    },
    "bow": {
        "pattern": r'\b(?:(?:High-Impact|Lightweight|Adaptative|Rapid-Fire|Rocket|Non-Burst|\d{3}RPM(?: and \d{3}RPM)*) )?Bows?\b',
        "class": "weapon-bow",
        "description": "Bow weapon type"
    },
    "linear_fusion_rifle": {
        "pattern": r'\b(?:(?:High-Impact|Lightweight|Adaptative|Rapid-Fire|Rocket|Non-Burst|\d{3}RPM(?: and \d{3}RPM)*) )?(?:Linear|LFRs?)(?: Fusion)?(?: Rifles?)?\b',
        "class": "weapon-linear-fusion-rifle",
        "description": "Linear Fusion Rifle weapon type"
    },
    "fusion_rifle": {
        "pattern": r'\b(?:(?:High-Impact|Lightweight|Adaptative|Rapid-Fire|Rocket|Non-Burst|\d{3}RPM(?: and \d{3}RPM)*) )?Fusion Rifles?\b',
        "class": "weapon-fusion-rifle",
        "description": "Fusion Rifle weapon type (excludes Linear)"
    },
    "sniper_rifle": {
        "pattern": r'\b(?:(?:High-Impact|Lightweight|Adaptative|Rapid-Fire|Rocket|Non-Burst|\d{3}RPM(?: and \d{3}RPM)*) )?Sniper Rifles?\b',
        "class": "weapon-sniper-rifle",
        "description": "Sniper Rifle weapon type"
    },
    "shotgun": {
        "pattern": r'\b(?:(?:High-Impact|Lightweight|Adaptative|Rapid-Fire|Rocket|Non-Burst|\d{3}RPM(?: and \d{3}RPM)*) )?Shotguns?\b',
        "class": "weapon-shotgun",
        "description": "Shotgun weapon type"
    },
    "trace_rifle": {
        "pattern": r'\b(?:(?:High-Impact|Lightweight|Adaptative|Rapid-Fire|Rocket|Non-Burst|\d{3}RPM(?: and \d{3}RPM)*) )?Trace Rifles?\b',
        "class": "weapon-trace-rifle",
        "description": "Trace Rifle weapon type"
    },
    "glaive": {
        "pattern": r'\b(?:(?:High-Impact|Lightweight|Adaptative|Rapid-Fire|Rocket|Non-Burst|\d{3}RPM(?: and \d{3}RPM)*) )?Glaives?\b',
        "class": "weapon-glaive",
        "description": "Glaive weapon type"
    },
    "heavy_grenade_launcher": {
        "pattern": r'\b(?:(?:(?:High-Impact|Adaptative|Rapid-Fire|Heavy|Rocket|Non-Burst|\d{3}RPM(?: and \d{3}RPM)*) )?Grenade Launchers?|GLs?|both GLs)\b',
        "class": "weapon-heavy-grenade-launcher",
        "description": "Heavy Grenade Launcher weapon type"
    },
    "grenade_launcher": {
        "pattern": r'\b(?:(?:(?:High-Impact|Lightweight|Rapid-Fire|Area-Denial|Rocket|Non-Burst|\d{3}RPM(?: and \d{3}RPM)*) )?Grenade Launchers?)\b',
        "class": "weapon-grenade-launcher",
        "description": "Grenade Launcher weapon type"
    },
    "rocket_launcher": {
        "pattern": r'\b(?:(?:High-Impact|Lightweight|Rapid-Fire|Rocket|Non-Burst|\d{3}RPM(?: and \d{3}RPM)*) )?Rocket Launchers?|RLs?\b',
        "class": "weapon-rocket-launcher",
        "description": "Rocket Launcher weapon type"
    },
    "machine_gun": {
        "pattern": r'\b(?:(?:High-Impact|Lightweight|Rapid-Fire|Rocket|Non-Burst|\d{3}RPM(?: and \d{3}RPM)*) )?Machine Guns?|MGs?\b',
        "class": "weapon-machine-gun",
        "description": "Machine Gun weapon type"
    },
    "sword": {
        "pattern": r'\b(?:(?:High-Impact|Lightweight|Rapid-Fire|Rocket|Non-Burst|\d{3}RPM(?: and \d{3}RPM)*) )?Swords?\b',
        "class": "weapon-sword",
        "description": "Sword weapon type"
    },
}

# =============================================================================
# PATTERN APPLICATION ORDER
# =============================================================================

# Order of pattern application (important for overlapping matches)
STYLES_ORDER = [
    # Values first (most specific)
    "pvp_value",
    "enhanced_arrow_text",
    "enhanced_arrow_value",

    # Elements
    "solar_keywords",
    "arc_keywords",
    "void_keywords",
    "stasis_keywords",
    "strand_keywords",
    "kinetic_keywords",
    "prismatic_keywords",

    # Champions
    "barrier_champion",
    "overload_champion",
    "unstoppable_champion",

    # Weapon types (specific to general)
    "auto_rifle",
    "pulse_rifle",
    "scout_rifle",
    "hand_cannon",
    "submachine_gun",
    "sidearm",
    "bow",
    "linear_fusion_rifle",
    "fusion_rifle",
    "sniper_rifle",
    "shotgun",
    "heavy_grenade_launcher",
    "grenade_launcher",
    "rocket_launcher",
    "machine_gun",
    "trace_rifle",
    "glaive",
    "sword",

    # Ammo types (last, most general)
    "primary_ammo",
    "special_ammo",
    "heavy_ammo",
]