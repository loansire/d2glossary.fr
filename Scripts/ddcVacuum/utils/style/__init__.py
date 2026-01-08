"""
Style module - Pattern matching and Clarity format processing

This module handles:
- Style pattern definitions (damage types, elements, keywords)
- Text processing with CSS class application
- Clarity format conversion (linesContent structure)
- Description formatting with paragraph/line separation

Submodules:
    patterns: Style pattern definitions and application order
    processors: Text processing and segment creation
    clarity: Clarity-specific format converters

Usage:
    from utils.style import (
        STYLE_PATTERNS,
        STYLES_ORDER,
        text_to_clarity_line,
        description_to_clarity_format
    )
"""

from utils.style.patterns import STYLE_PATTERNS, STYLES_ORDER
from utils.style.processors import text_to_clarity_line
from utils.style.clarity import (
    description_to_clarity_format,
    record_to_clarity_format,
    records_to_clarity_json
)

__all__ = [
    # Patterns
    "STYLE_PATTERNS",
    "STYLES_ORDER",

    # Processors
    "text_to_clarity_line",

    # Clarity format
    "description_to_clarity_format",
    "record_to_clarity_format",
    "records_to_clarity_json",
]