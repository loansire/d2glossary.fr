"""
Styles configuration for DDCVacuum - Clarity Format Compatible
Produces JSON output matching D2Clarity's linesContent structure
"""
import re
from typing import Any


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
        "pattern": r'\b(Fist of Havoc|Speed Booster|Thundercrash|Ionic Traces?|Stormtrance|Bolt Charge|Arc Staff|Jolt Shot|Amplified|Blinded|Jolting|Jolted|Blind|Jolt|Arc)\b',
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
        "pattern": r'\bSpecial (?:Ammo(?: (?:Reserves?|Weapons?|Bricks?))?|Weapons?)\b',
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
        "pattern": r'\b(?:(?:High-Impact|Lightweight|Rapid-Fire|Rocket|Non-Burst|\d{3}RPM) )?Auto Rifles?\b',
        "class": "weapon-auto-rifle",
        "description": "Auto Rifle weapon type"
    },
    "pulse_rifle": {
        "pattern": r'\b(?:(?:High-Impact|Lightweight|Rapid-Fire|Rocket|Non-Burst|\d{3}RPM) )?Pulse(?: Rifles?)?\b',
        "class": "weapon-pulse-rifle",
        "description": "Pulse Rifle weapon type"
    },
    "scout_rifle": {
        "pattern": r'\b(?:(?:High-Impact|Lightweight|Rapid-Fire|Rocket|Non-Burst|\d{3}RPM) )?Scout Rifles?\b',
        "class": "weapon-scout-rifle",
        "description": "Scout Rifle weapon type"
    },
    "hand_cannon": {
        "pattern": r'\b(?:(?:High-Impact|Lightweight|Rapid-Fire|Rocket|Non-Burst|\d{3}RPM) )?Hand Cannons?\b',
        "class": "weapon-hand-cannon",
        "description": "Hand Cannon weapon type"
    },
    "sidearm": {
        "pattern": r'\b(?:(?:High-Impact|Lightweight|Rapid-Fire|Rocket|Non-Burst|\d{3}RPM) )?Sidearms?\b',
        "class": "weapon-sidearm",
        "description": "Sidearm weapon type"
    },
    "submachine_gun": {
        "pattern": r'\b(?:(?:(?:High-Impact|Lightweight|Rapid-Fire|Rocket|Non-Burst|\d{3}RPM) )?Submachine Guns?|SMGs?)\b',
        "class": "weapon-smg",
        "description": "Submachine Gun weapon type"
    },
    "bow": {
        "pattern": r'\b(?:(?:High-Impact|Lightweight|Rapid-Fire|Rocket|Non-Burst|\d{3}RPM) )?Bows?\b',
        "class": "weapon-bow",
        "description": "Bow weapon type"
    },
    "fusion_rifle": {
        "pattern": r'\b(?:(?:High-Impact|Lightweight|Rapid-Fire|Rocket|Linear|Non-Burst|\d{3}RPM) )?Fusion Rifles?\b',
        "class": "weapon-fusion-rifle",
        "description": "Fusion Rifle weapon type"
    },
    "sniper_rifle": {
        "pattern": r'\b(?:(?:High-Impact|Lightweight|Rapid-Fire|Rocket|Non-Burst|\d{3}RPM) )?Sniper Rifles?\b',
        "class": "weapon-sniper-rifle",
        "description": "Sniper Rifle weapon type"
    },
    "shotgun": {
        "pattern": r'\b(?:(?:High-Impact|Lightweight|Rapid-Fire|Rocket|Non-Burst|\d{3}RPM) )?Shotguns?\b',
        "class": "weapon-shotgun",
        "description": "Shotgun weapon type"
    },
    "trace_rifle": {
        "pattern": r'\b(?:(?:High-Impact|Lightweight|Rapid-Fire|Rocket|Non-Burst|\d{3}RPM) )?Trace Rifles?\b',
        "class": "weapon-trace-rifle",
        "description": "Trace Rifle weapon type"
    },
    "glaive": {
        "pattern": r'\b(?:(?:High-Impact|Lightweight|Rapid-Fire|Rocket|Non-Burst|\d{3}RPM) )?Glaives?\b',
        "class": "weapon-glaive",
        "description": "Glaive weapon type"
    },
    "grenade_launcher": {
        "pattern": r'\b(?:(?:(?:High-Impact|Lightweight|Rapid-Fire|Rocket|Non-Burst|\d{3}RPM) )?Grenade Launchers?|GLs?|both GLs)\b',
        "class": "weapon-grenade-launcher",
        "description": "Grenade Launcher weapon type"
    },
    "rocket_launcher": {
        "pattern": r'\b(?:(?:High-Impact|Lightweight|Rapid-Fire|Rocket|Non-Burst|\d{3}RPM) )?Rocket Launchers?\b',
        "class": "weapon-rocket-launcher",
        "description": "Rocket Launcher weapon type"
    },
    "machine_gun": {
        "pattern": r'\b(?:(?:High-Impact|Lightweight|Rapid-Fire|Rocket|Non-Burst|\d{3}RPM) )?Machine Guns?\b',
        "class": "weapon-machine-gun",
        "description": "Machine Gun weapon type"
    },
    "sword": {
        "pattern": r'\b(?:(?:High-Impact|Lightweight|Rapid-Fire|Rocket|Non-Burst|\d{3}RPM) )?Swords?\b',
        "class": "weapon-sword",
        "description": "Sword weapon type"
    },
}

# Order of pattern application (important for overlapping matches)
STYLES_ORDER = [
    "pvp_value",
    "enhanced_arrow_text",
    "enhanced_arrow_value",
    "solar_keywords",
    "arc_keywords",
    "void_keywords",
    "stasis_keywords",
    "strand_keywords",
    "kinetic_keywords",
    "prismatic_keywords",
    "barrier_champion",
    "overload_champion",
    "unstoppable_champion",
    "primary_ammo",
    "special_ammo",
    "heavy_ammo",
    "auto_rifle",
    "pulse_rifle",
    "scout_rifle",
    "hand_cannon",
    "submachine_gun",
    "sidearm",
    "bow",
    "fusion_rifle",
    "sniper_rifle",
    "shotgun",
    "grenade_launcher",
    "rocket_launcher",
    "machine_gun",
    "trace_rifle",
    "glaive",
    "sword",
]


# =============================================================================
# CLARITY JSON CONVERTER
# =============================================================================

def text_to_clarity_line(text: str) -> list[dict[str, Any]]:
    """
    Convert a text string to Clarity's linesContent format.
    Returns a list of segments with text and optional classNames.

    Example output:
    [
        {"text": "Grants "},
        {"text": "20%", "classNames": ["pve"]},
        {"text": " "},
        {"text": "[15%]", "classNames": ["pvp"]},
        {"text": " increased damage"}
    ]
    """
    if not text or not isinstance(text, str):
        return [{"text": str(text) if text else ""}]

    segments = []
    current_pos = 0
    matches = []

    # Collect all matches with their positions
    for style_name in STYLES_ORDER:
        config = STYLE_PATTERNS.get(style_name)
        if not config:
            continue

        pattern = config["pattern"]
        css_class = config["class"]
        flags = config.get("flags", 0)

        for match in re.finditer(pattern, text, flags):
            capture_group = config.get("capture_group", 0)
            start, end = match.span(capture_group) if capture_group else match.span()
            matched_text = match.group(capture_group) if capture_group else match.group()

            matches.append({
                "start": start,
                "end": end,
                "text": matched_text,
                "class": css_class,
                "full_match": match.group(0),
                "full_start": match.start(),
                "full_end": match.end()
            })

    # Sort by position and remove overlaps (keep first match)
    matches.sort(key=lambda x: (x["start"], -x["end"]))
    filtered_matches = []
    last_end = 0

    for m in matches:
        if m["start"] >= last_end:
            filtered_matches.append(m)
            last_end = m["end"]

    # Build segments
    for m in filtered_matches:
        # Add plain text before this match
        if m["start"] > current_pos:
            plain_text = text[current_pos:m["start"]]
            if plain_text:
                segments.append({"text": plain_text})

        # Add styled segment
        segment = {"text": m["text"]}
        if m["class"]:
            segment["classNames"] = [m["class"]]
        segments.append(segment)

        current_pos = m["end"]

    # Add remaining text
    if current_pos < len(text):
        remaining = text[current_pos:]
        if remaining:
            segments.append({"text": remaining})

    # If no segments created, return the original text
    if not segments:
        return [{"text": text}]

    return segments


def description_to_clarity_format(description: str) -> list[dict[str, Any]]:
    """
    Convert a full description to Clarity's descriptions.en format.
    Splits by newlines and creates linesContent arrays with spacers.

    Example output:
    [
        {"linesContent": [{"text": "First line"}, {"text": " with ", "classNames": ["solar"]}, {"text": "style"}]},
        {"classNames": ["spacer"]},
        {"linesContent": [{"text": "Second paragraph"}]}
    ]
    """
    if not description or not isinstance(description, str):
        return []

    result = []

    # Split by double newlines (paragraphs) or single newlines
    # Clarity uses spacer objects between paragraphs
    paragraphs = re.split(r'\n\s*\n|\r\n\s*\r\n', description)

    for i, para in enumerate(paragraphs):
        if not para.strip():
            continue

        # Split paragraph into lines
        lines = para.strip().split('\n')

        for j, line in enumerate(lines):
            line = line.strip()
            if not line:
                continue

            # Convert line to Clarity format
            line_content = text_to_clarity_line(line)
            result.append({"linesContent": line_content})

        # Add spacer between paragraphs (not after the last one)
        if i < len(paragraphs) - 1:
            result.append({"classNames": ["spacer"]})

    return result


def record_to_clarity_format(record: dict, hash_key: str = "Hash") -> dict[str, Any]:
    """
    Convert a DDCVacuum record to Clarity JSON format.

    Input record example:
    {
        "Hash": 12345,
        "Name": "Rampage",
        "Description": "Kills grant damage...",
        "Type": "Weapon Trait"
    }

    Output Clarity format:
    {
        "12345": {
            "hash": 12345,
            "name": "Rampage",
            "type": "Weapon Trait",
            "descriptions": {
                "en": [
                    {"linesContent": [{"text": "Kills grant damage..."}]}
                ]
            }
        }
    }
    """
    hash_value = record.get(hash_key, record.get("hash", 0))
    name = record.get("Name", record.get("name", ""))
    description = record.get("Description", record.get("description", ""))
    perk_type = record.get("Type", record.get("type", ""))

    clarity_record = {
        "hash": hash_value,
        "name": name,
        "type": perk_type,
        "descriptions": {
            "en": description_to_clarity_format(description)
        }
    }

    # Add optional fields if present
    if "itemHash" in record:
        clarity_record["itemHash"] = record["itemHash"]
    if "itemName" in record:
        clarity_record["itemName"] = record["itemName"]

    return {str(hash_value): clarity_record}


def records_to_clarity_json(records: list[dict], hash_key: str = "Hash") -> dict[str, Any]:
    """
    Convert a list of records to a full Clarity-compatible JSON structure.
    """
    result = {}

    for record in records:
        clarity_record = record_to_clarity_format(record, hash_key)
        result.update(clarity_record)

    return result


# =============================================================================
# UTILITY FUNCTIONS
# =============================================================================

def add_link(text: str, url: str) -> dict[str, Any]:
    """Create a link segment in Clarity format"""
    return {
        "text": text,
        "link": url,
        "classNames": ["link"]
    }


def add_tooltip(text: str, tooltip_content: list[dict]) -> dict[str, Any]:
    """Create a tooltip segment in Clarity format"""
    return {
        "text": text,
        "title": tooltip_content,
        "classNames": ["title"]
    }


def create_spacer() -> dict[str, Any]:
    """Create a spacer element"""
    return {"classNames": ["spacer"]}