"""
Utils package for DDCVacuum
Provides modular data processing pipeline: Fetch → Filter → Transform → Export

Modules:
    fetch: Data retrieval from Google Sheets
    transform: Data transformation and stylization
    style: Style patterns and Clarity format processing
    export: JSON export and preview server

Usage:
    from utils import (
        # Configuration
        SHEETS, OUTPUT_DIR,

        # Fetch
        fetch_sheet,

        # Transform
        stylize_records,

        # Export
        save_json, start_preview_server
    )
"""

# =============================================================================
# FETCH MODULE - Data retrieval
# =============================================================================
from utils.fetch.config import SHEETS, OUTPUT_DIR, SHEET_ID
from utils.fetch.google_sheets import fetch_sheet

# =============================================================================
# TRANSFORM MODULE - Data transformation
# =============================================================================
from utils.transform.stylizer import stylize_records

# =============================================================================
# EXPORT MODULE - Output generation
# =============================================================================
from utils.export.json_writer import save_json, clean_nan_values
from utils.export.server import start_preview_server

# =============================================================================
# PUBLIC API
# =============================================================================
__all__ = [
    # Configuration
    "SHEETS",
    "OUTPUT_DIR",
    "SHEET_ID",

    # Fetch
    "fetch_sheet",

    # Transform
    "stylize_records",

    # Export
    "save_json",
    "clean_nan_values",
    "start_preview_server",
]