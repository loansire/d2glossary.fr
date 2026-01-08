# Utils Module - DDCVacuum

Module de traitement des données DDCVacuum organisé en pipeline modulaire :

```
Fetch → (Filters) → Transform → Export
```

## 📁 Structure

```
utils/
├── __init__.py              # Point d'entrée avec API publique
├── README.md                # Ce fichier
│
├── fetch/                   # 📥 Récupération des données
│   ├── __init__.py
│   ├── config.py            # Configuration Google Sheets
│   └── google_sheets.py     # Récupération via API
│
├── transform/               # 🔄 Transformation des données
│   ├── __init__.py
│   └── stylizer.py          # Ajout des styles Clarity
│
├── style/                   # 🎨 Gestion des styles
│   ├── __init__.py
│   ├── patterns.py          # Définition des patterns
│   ├── processors.py        # Traitement du texte
│   └── clarity.py           # Formats Clarity
│
└── export/                  # 💾 Export des données
    ├── __init__.py
    ├── json_writer.py       # Écriture JSON
    └── server.py            # Serveur de prévisualisation
```

## 🚀 Utilisation rapide

### Import simplifié

```python
from utils import (
    # Configuration
    SHEETS, OUTPUT_DIR,
    
    # Pipeline
    fetch_sheet,
    stylize_records,
    save_json
)

# Récupération
records = fetch_sheet("WeaponPerks", SHEETS["WeaponPerks"])

# Transformation
styled_records = stylize_records(records)

# Export
save_json(styled_records, f"{OUTPUT_DIR}/WeaponPerks_styled.json")
```

### Import par module

```python
# Fetch
from utils.fetch import fetch_sheet, SHEETS, OUTPUT_DIR

# Transform
from utils.transform import stylize_records

# Style (pour usage avancé)
from utils.style import STYLE_PATTERNS, text_to_clarity_line

# Export
from utils.export import save_json, start_preview_server
```

## 📦 Modules détaillés

### 1️⃣ Fetch - Récupération des données

**Responsabilité** : Récupérer les données depuis Google Sheets et les convertir en records Python.

#### Configuration (`fetch/config.py`)

```python
SHEET_ID = "1tfa3mEwTWLrPUEw2p9aRKWUH37quVgpkyVisB6E1DZU"

SHEETS = {
    "WeaponPerks": "1703329297",
    "ArmorSets": "1916736284",
    # ...
}

OUTPUT_DIR = "data"
```

#### Récupération (`fetch/google_sheets.py`)

```python
from utils.fetch import fetch_sheet

records = fetch_sheet("WeaponPerks", "1703329297")
# Retourne: [{"Name": "...", "Description": "...", ...}, ...]
```

**Fonctionnalités** :
- Téléchargement CSV depuis Google Sheets
- Parsing avec pandas
- Conversion en liste de dictionnaires
- Gestion des erreurs réseau

---

### 2️⃣ Transform - Transformation des données

**Responsabilité** : Enrichir les records avec des données stylisées pour Clarity.

#### Stylisation (`transform/stylizer.py`)

```python
from utils.transform import stylize_records

styled = stylize_records(raw_records)
```

**Transformation** :
```python
# Input
{
    "Name": "Rampage",
    "Description": "Kills grant 10% [5%] damage."
}

# Output
{
    "Name": "Rampage",
    "Description": "Kills grant 10% [5%] damage.",
    "descriptions": {
        "en": [
            {
                "linesContent": [
                    {"text": "Kills grant "},
                    {"text": "10%", "classNames": ["pve"]},
                    {"text": " "},
                    {"text": "[5%]", "classNames": ["pvp"]},
                    {"text": " damage."}
                ]
            }
        ]
    }
}
```

---

### 3️⃣ Style - Gestion des styles

**Responsabilité** : Appliquer les patterns CSS aux descriptions textuelles.

#### Patterns (`style/patterns.py`)

Définit les regex et classes CSS pour identifier :
- Éléments (Solar, Arc, Void, Stasis, Strand, Prismatic, Kinetic)
- Champions (Barrier, Unstoppable, Overload)
- Types de dégâts (Kinetic, Energy, Power, Heavy)
- Types d'armes (Auto Rifle, Scout Rifle, etc.)
- Valeurs PvE/PvP
- Perks Enhanced (↑)

```python
STYLE_PATTERNS = {
    "solar_keywords": {
        "pattern": r'\b(Solar|Scorch|Ignite|...)\b',
        "class": "solar"
    },
    # ...
}

STYLES_ORDER = [
    "enhanced_arrow_text",
    "enhanced_arrow_value",
    "pvp_value",
    "solar_keywords",
    # ...
]
```

#### Processors (`style/processors.py`)

```python
from utils.style import text_to_clarity_line

segments = text_to_clarity_line("Grants Solar damage")
# [
#     {"text": "Grants "},
#     {"text": "Solar", "classNames": ["solar"]},
#     {"text": " damage"}
# ]
```

#### Clarity (`style/clarity.py`)

Formats spécifiques à D2Clarity :

```python
from utils.style import description_to_clarity_format

clarity_format = description_to_clarity_format(
    "First paragraph.\n\nSecond paragraph."
)
# [
#     {"linesContent": [{"text": "First paragraph."}]},
#     {"classNames": ["spacer"]},
#     {"linesContent": [{"text": "Second paragraph."}]}
# ]
```

---

### 4️⃣ Export - Export des données

**Responsabilité** : Sauvegarder les données en JSON et fournir un serveur de prévisualisation.

#### JSON Writer (`export/json_writer.py`)

```python
from utils.export import save_json

save_json(data, "output.json")
```

**Fonctionnalités** :
- Nettoyage automatique des valeurs NaN/None
- Formatage JSON lisible (indent=2)
- Support UTF-8

#### Server (`export/server.py`)

```python
from utils.export import start_preview_server

start_preview_server(port=8000)
# Démarre un serveur HTTP sur http://localhost:8000
```

---

## 🔄 Flux de traitement complet

```python
from utils import (
    SHEETS, OUTPUT_DIR,
    fetch_sheet,
    stylize_records,
    save_json
)
from filters.pipeline import apply_filters_if_configured

# 1. Récupération
records = fetch_sheet("WeaponPerks", SHEETS["WeaponPerks"])

# 2. Filtrage (optionnel)
records = apply_filters_if_configured("WeaponPerks", records)

# 3. Stylisation
styled = stylize_records(records)

# 4. Export
save_json(records, f"{OUTPUT_DIR}/simple/WeaponPerks.json")
save_json(styled, f"{OUTPUT_DIR}/styled/WeaponPerks_styled.json")
```

---

## 🎯 Principes de conception

### Modularité
Chaque module a une responsabilité unique et peut être utilisé indépendamment.

### Réutilisabilité
Les fonctions sont conçues pour être utilisées dans différents contextes.

### Harmonisation
Architecture cohérente avec le module `filters/` existant.

### Documentation
Chaque module et fonction est documenté avec des docstrings claires.

---

## 🔧 Extension

### Ajouter un nouveau style pattern

1. **Éditer `style/patterns.py`** :
```python
STYLE_PATTERNS["mon_pattern"] = {
    "pattern": r'\b(Keyword1|Keyword2)\b',
    "class": "ma-classe"
}

STYLES_ORDER.append("mon_pattern")
```

2. **Le pattern sera automatiquement appliqué** lors de la stylisation.

### Ajouter une nouvelle source de données

1. **Créer un nouveau fichier dans `fetch/`** :
```python
# fetch/api_bungie.py
def fetch_bungie_data(endpoint: str) -> list[dict]:
    # Logique de récupération
    pass
```

2. **Exposer dans `fetch/__init__.py`** :
```python
from utils.fetch.api_bungie import fetch_bungie_data

__all__ = [..., "fetch_bungie_data"]
```

---

## 📚 Voir aussi

- [`filters/README.md`](../filters/README.md) - Documentation du système de filtres
- [`main.py`](../main.py) - Point d'entrée principal du programme
- [Google Sheets DDCVacuum Panel](https://docs.google.com/spreadsheets/d/1tfa3mEwTWLrPUEw2p9aRKWUH37quVgpkyVisB6E1DZU/)

---

## 🤝 Bonnes pratiques

1. **Immutabilité** : Toujours copier les records avant modification
2. **Gestion d'erreurs** : Utiliser try/except appropriés
3. **Types** : Utiliser les type hints pour la clarté
4. **Tests** : Tester avec des cas limites (None, "", NaN)
5. **Documentation** : Documenter les fonctions publiques