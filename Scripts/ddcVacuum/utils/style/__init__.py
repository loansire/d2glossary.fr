"""
Style module - Pattern matching and DDCVacuum format processing

This module handles:
- Style pattern definitions (damage types, elements, keywords)
- Text processing with CSS class application
- DDCVacuum format conversion (linesContent structure)
- Description formatting with paragraph/line separation

Submodules:
    patterns: Style pattern definitions and application order
    processors: Text processing and segment creation
    ddcvacuum: DDCVacuum-specific format converters

Usage:
    from utils.style import (
        STYLE_PATTERNS,
        STYLES_ORDER,
        text_to_ddcvacuum_line,
        description_to_ddcvacuum_format
    )
"""

from utils.style.patterns import STYLE_PATTERNS, STYLES_ORDER
from utils.style.processors import text_to_ddcvacuum_line
from utils.style.ddcvacuum import (
    description_to_ddcvacuum_format,
    record_to_ddcvacuum_format,
    records_to_ddcvacuum_json
)

__all__ = [
    # Patterns
    "STYLE_PATTERNS",
    "STYLES_ORDER",

    # Processors
    "text_to_ddcvacuum_line",

    # DDCVacuum format
    "description_to_ddcvacuum_format",
    "record_to_ddcvacuum_format",
    "records_to_ddcvacuum_json",
]