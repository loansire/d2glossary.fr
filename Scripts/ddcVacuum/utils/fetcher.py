import pandas as pd
from utils.config import SHEET_ID


def fetch_sheet(name: str, gid: str) -> list[dict]:
    """Récupère une sheet Google et retourne une liste de dicts"""
    url = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/export?format=csv&gid={gid}"

    df = pd.read_csv(url)
    records = df.to_dict(orient="records")

    return records