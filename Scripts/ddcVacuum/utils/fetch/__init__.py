"""
Fetch module - Data retrieval from Google Sheets

This module handles:
- Google Sheets API configuration
- Sheet data fetching with proper formatting
- CSV parsing and record conversion

Usage:
    from utils.fetch import fetch_sheet, SHEETS, OUTPUT_DIR

    records = fetch_sheet("WeaponPerks", SHEETS["WeaponPerks"])
"""

from utils.fetch.config import SHEETS, OUTPUT_DIR, SHEET_ID
from utils.fetch.google_sheets import fetch_sheet

__all__ = [
    "SHEETS",
    "OUTPUT_DIR",
    "SHEET_ID",
    "fetch_sheet",
]