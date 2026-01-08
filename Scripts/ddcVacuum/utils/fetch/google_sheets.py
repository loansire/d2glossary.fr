"""
Google Sheets data fetcher

Retrieves data from Google Sheets and converts to Python records
"""

import pandas as pd
from utils.fetch.config import SHEET_ID


def fetch_sheet(name: str, gid: str) -> list[dict]:
    """
    Récupère une sheet Google et retourne une liste de dictionnaires

    Args:
        name: Nom de la sheet (pour référence)
        gid: ID de la sheet (tab identifier)

    Returns:
        Liste de dictionnaires représentant les enregistrements

    Raises:
        Exception: Si l'URL est invalide ou la récupération échoue

    Example:
        >>> records = fetch_sheet("WeaponPerks", "1703329297")
        >>> print(len(records))
        150
    """
    # Construire l'URL d'export CSV
    url = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/export?format=csv&gid={gid}"

    # Lire le CSV avec pandas
    df = pd.read_csv(url)

    # Convertir en liste de dictionnaires
    records = df.to_dict(orient="records")

    return records