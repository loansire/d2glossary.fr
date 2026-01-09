"""
Hash Enricher Module
Enriches ddcVacuum data with hashes from d2glossary

Usage:
    from hash_enricher import HashEnricher, HASH_MAPPINGS

    enricher = HashEnricher()
    result = enricher.enrich_sheet("ArmorSets")
    enricher.save_enriched("ArmorSets")
    enricher.print_report("ArmorSets")
"""

from .config import (
    D2GLOSSARY_BASE,
    DDCVACUUM_BASE,
    HASH_MAPPINGS,
    get_nested_value,
    set_nested_value
)
from .matcher import (
    find_hash_matches,
    enrich_record_with_hashes
)
from .recover import HashEnricher

__all__ = [
    # Configuration
    "D2GLOSSARY_BASE",
    "DDCVACUUM_BASE",
    "HASH_MAPPINGS",
    "get_nested_value",
    "set_nested_value",

    # Matcher functions
    "find_hash_matches",
    "enrich_record_with_hashes",

    # Main class
    "HashEnricher",
]