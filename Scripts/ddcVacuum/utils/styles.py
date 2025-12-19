"""
Styles configuration for DDCVacuum - Clarity Format Compatible
Produces JSON output matching D2Clarity's linesContent structure
"""
import re
from typing import Any

# =============================================================================
# CLARITY CLASS NAMES - Match exactly what Clarity uses
# =============================================================================

CLARITY_CLASSES = {
    # Elements / Subclasses
    "solar": "solar",
    "arc": "arc",
    "void": "void",
    "stasis": "stasis",
    "strand": "strand",

    # Game modes
    "pve": "pve",
    "pvp": "pvp",

    # Special formatting
    "spacer": "spacer",
    "link": "link",
    "title": "title",

    # Ammo types
    "primary": "primary",
    "special": "special",
    "heavy": "heavy",

    # Champions
    "barrier": "barrier",
    "overload": "overload",
    "unstoppable": "unstoppable",

    # Enhanced perks
    "enhancedArrow": "enhancedArrow",

    # Custom additions (not in original Clarity but useful)
    "yellow": "yellow",  # For exotic names
}

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
        "description": "PVP-specific values in brackets - captures everything between []"
    },

    # === ELEMENTS / SUBCLASSES ===
    "solar_keywords": {
        "pattern": r'\b(Well of Radiance|Blade Barrage|Song of Flame|Ember of \w+|Firesprites|Firesprite|Restoration|Scorching|Ignition|Scorched|Daybreak|Golden Gun|Ignited|Ignites|Radiant|Ignite|Scorch|Solar|Cure)\b',
        "class": "solar",
        "description": "Solar subclass keywords"
    },
    "arc_keywords": {
        "pattern": r'\b(Fist of Havoc|Speed Booster|Thundercrash|Ionic Traces|Stormtrance|Bolt Charge|Ionic Trace|Arc Staff|Jolt Shot|Amplified|Blinded|Jolting|Jolted|Blind|Jolt|Arc)\b',
        "class": "arc",
        "description": "Arc subclass keywords"
    },
    "void_keywords": {
        "pattern": r'\b(Chaos Accelerant|Void Overshield|Void Breaches|Invisibility|Suppression|Suppressed|Void Breach|Echo of \w+|Smoke Bomb|Weakening|Invisible|Weakened|Volatile|Overshield|Suppress|Devour|Weaken|Void)\b',
        "class": "void",
        "description": "Void subclass keywords"
    },
    "stasis_keywords": {
        "pattern": r'\b(Stasis Crystals|Stasis Crystal|Stasis Seeker|Stasis Debuff|Whisper of \w+|Stasis Shards|Glacial Guard|Frost Armor|Stasis Shard|Shattering|Shattered|Shatter|Slowed|Frozen|Freeze|Stasis|Slow)\b',
        "class": "stasis",
        "description": "Stasis subclass keywords"
    },
    "strand_keywords": {
        "pattern": r'\b(Unraveling Rounds|Thread of \w+|Threadlings|Woven Mail|Threadling|Unraveling|Suspended|Unravel|Tangles|Severed|Suspend|Tangle|Strand|Sever)\b',
        "class": "strand",
        "description": "Strand subclass keywords"
    },

    # === CHAMPIONS ===
    "barrier_champion": {
        "pattern": r'\b(Barrier Champions?|Barrier Champion\'?s?)\b',
        "class": "barrier",
        "description": "Barrier champion references"
    },
    "overload_champion": {
        "pattern": r'\b(Overload Champions?|Overload Champion\'?s?|Disruption)\b',
        "class": "overload",
        "description": "Overload champion references"
    },
    "unstoppable_champion": {
        "pattern": r'\b(Unstoppable Champions?|Unstoppable Champion\'?s?)\b',
        "class": "unstoppable",
        "description": "Unstoppable champion references"
    },

    # === AMMO TYPES ===
    "primary_ammo": {
        "pattern": r'\b(Primary Weapons?|Primary Ammo)\b',
        "class": "primary",
        "description": "Primary ammo type"
    },
    "special_ammo": {
        "pattern": r'\b(Special Weapons?|Special Ammo)\b',
        "class": "special",
        "description": "Special ammo type"
    },
    "heavy_ammo": {
        "pattern": r'\b(Power Weapons?|Heavy Weapons?|Heavy Ammo)\b',
        "class": "heavy",
        "description": "Heavy/Power ammo type"
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
    "barrier_champion",
    "overload_champion",
    "unstoppable_champion",
    "primary_ammo",
    "special_ammo",
    "heavy_ammo",
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
# CSS STYLES (for HTML preview)
# =============================================================================

CSS_STYLES = """
:root {
    --color-solar: #ff6b35;
    --color-arc: #7ec8e3;
    --color-void: #b388ff;
    --color-stasis: #4fc3f7;
    --color-strand: #66bb6a;
    --color-pve: #74c0fc;
    --color-pvp: #ff6b6b;
    --color-primary: #c8c8c8;
    --color-special: #7cfc00;
    --color-heavy: #9370db;
    --color-barrier: #ff4081;
    --color-overload: #00bcd4;
    --color-unstoppable: #ff9800;
    --color-enhanced: #ffd700;
    --color-yellow: #ffd43b;
}

.solar { color: var(--color-solar); font-weight: 500; }
.arc { color: var(--color-arc); font-weight: 500; }
.void { color: var(--color-void); font-weight: 500; }
.stasis { color: var(--color-stasis); font-weight: 500; }
.strand { color: var(--color-strand); font-weight: 500; }
.pve { color: var(--color-pve); }
.pvp { color: var(--color-pvp); }
.primary { color: var(--color-primary); }
.special { color: var(--color-special); }
.heavy { color: var(--color-heavy); }
.barrier { color: var(--color-barrier); font-weight: bold; }
.overload { color: var(--color-overload); font-weight: bold; }
.unstoppable { color: var(--color-unstoppable); font-weight: bold; }
.enhancedArrow { color: var(--color-enhanced); font-weight: bold; }
.yellow { color: var(--color-yellow); }
.spacer { display: block; height: 0.5em; }
.link { color: #74c0fc; text-decoration: underline; cursor: pointer; }
.title { border-bottom: 1px dotted currentColor; cursor: help; }
"""


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