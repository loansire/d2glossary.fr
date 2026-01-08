"""
Transform module - Data transformation and stylization

This module handles:
- Converting raw records to styled format
- Adding Clarity-formatted descriptions
- Maintaining record structure while enriching with style data

Usage:
    from utils.transform import stylize_records

    styled = stylize_records(raw_records)
"""

from utils.transform.stylizer import stylize_records

__all__ = [
    "stylize_records",
]