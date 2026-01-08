# ✅ Checklist de vérification - Migration utils/

## 📋 Avant de commencer

- [ ] Tous les nouveaux fichiers sont créés
- [ ] La structure de dossiers est en place
- [ ] Les anciens fichiers sont toujours présents (pour comparaison)

## 🔍 Tests d'imports

### Test 1 : Import via utils/__init__.py
```python
# test_imports.py
from utils import (
    SHEETS, OUTPUT_DIR, SHEET_ID,
    fetch_sheet,
    stylize_records,
    save_json,
    start_preview_server
)

print("✓ Import via utils/__init__.py réussi")
print(f"✓ SHEETS contient {len(SHEETS)} sheets")
print(f"✓ OUTPUT_DIR = {OUTPUT_DIR}")
```

**Résultat attendu** :
```
✓ Import via utils/__init__.py réussi
✓ SHEETS contient 12 sheets
✓ OUTPUT_DIR = data
```

- [ ] Test 1 réussi

---

### Test 2 : Import par module
```python
# test_module_imports.py
from utils.fetch import fetch_sheet, SHEETS, OUTPUT_DIR
from utils.transform import stylize_records
from utils.style import text_to_clarity_line, description_to_clarity_format
from utils.export import save_json, clean_nan_values

print("✓ Tous les imports modulaires réussis")
```

**Résultat attendu** :
```
✓ Tous les imports modulaires réussis
```

- [ ] Test 2 réussi

---

### Test 3 : Test de fetch_sheet
```python
# test_fetch.py
from utils import fetch_sheet, SHEETS

try:
    records = fetch_sheet("WeaponPerks", SHEETS["WeaponPerks"])
    print(f"✓ fetch_sheet fonctionne : {len(records)} records récupérés")
    print(f"✓ Premier record : {list(records[0].keys())}")
except Exception as e:
    print(f"✗ Erreur : {e}")
```

**Résultat attendu** :
```
✓ fetch_sheet fonctionne : 150+ records récupérés
✓ Premier record : ['Name', 'Description', 'Type', ...]
```

- [ ] Test 3 réussi

---

### Test 4 : Test de stylize_records
```python
# test_stylize.py
from utils import stylize_records

test_record = {
    "Name": "Rampage",
    "Description": "Grants Solar damage"
}

styled = stylize_records([test_record])
print(f"✓ stylize_records fonctionne")
print(f"✓ Descriptions ajoutées : {'descriptions' in styled[0]}")

if 'descriptions' in styled[0]:
    desc = styled[0]['descriptions']['en']
    print(f"✓ Format Clarity : {type(desc)} avec {len(desc)} éléments")
```

**Résultat attendu** :
```
✓ stylize_records fonctionne
✓ Descriptions ajoutées : True
✓ Format Clarity : <class 'list'> avec 1 éléments
```

- [ ] Test 4 réussi

---

### Test 5 : Test de save_json
```python
# test_save.py
import os
from utils import save_json, clean_nan_values

test_data = {
    "valid": "data",
    "none_value": None,
    "nan_value": "NaN",
    "empty": ""
}

save_json(test_data, "test_output.json")

if os.path.exists("test_output.json"):
    print("✓ save_json fonctionne")
    with open("test_output.json", "r") as f:
        import json
        saved = json.load(f)
        print(f"✓ Données sauvegardées : {saved}")
        print(f"✓ NaN/None/empty nettoyés : {len(saved) == 1}")
    os.remove("test_output.json")
```

**Résultat attendu** :
```
✓ save_json fonctionne
✓ Données sauvegardées : {'valid': 'data'}
✓ NaN/None/empty nettoyés : True
```

- [ ] Test 5 réussi

---

### Test 6 : Test des patterns
```python
# test_patterns.py
from utils.style import text_to_clarity_line

test_cases = [
    "Grants Solar damage",
    "Deals 10% [5%] damage",
    "Barrier Champions are stunned"
]

for text in test_cases:
    segments = text_to_clarity_line(text)
    has_classes = any('classNames' in seg for seg in segments)
    print(f"✓ '{text}' → {len(segments)} segments (styled: {has_classes})")
```

**Résultat attendu** :
```
✓ 'Grants Solar damage' → 3 segments (styled: True)
✓ 'Deals 10% [5%] damage' → 4 segments (styled: True)
✓ 'Barrier Champions are stunned' → 3 segments (styled: True)
```

- [ ] Test 6 réussi

---

## 🚀 Test du pipeline complet

### Test 7 : Exécution de main.py
```bash
python main.py
```

**Résultat attendu** :
```
==============================================================
🔧 Configuration requise
...
🚀 Démarrage de l'export D2 Glossary

📥 Récupération de WeaponPerks...
   ✓ WeaponPerks (150 items)
📥 Récupération de ArmorSets...
   🔧 Application des filtres...
      → Filtre 1/3: NamePropagationFilter
      → Filtre 2/3: NameCommentSplitFilter
      → Filtre 3/3: ArmorSetDescriptionSplitFilter
   ✓ ArmorSets (50 items)
...

✅ Export terminé!
   📁 data/simple/ (12 fichiers)
   📁 data/styled/ (12 fichiers)
   📄 data/all_data.json
   📄 data/all_data_styled.json
```

- [ ] Test 7 réussi
- [ ] Aucune erreur d'import
- [ ] Tous les fichiers générés

---

## 📊 Vérification des outputs

### Test 8 : Comparaison des outputs
```python
# test_compare_outputs.py
import json

# Charger les nouveaux fichiers
with open("data/all_data.json", "r") as f:
    new_data = json.load(f)

with open("data/all_data_styled.json", "r") as f:
    new_styled = json.load(f)

print(f"✓ all_data.json : {len(new_data)} sheets")
print(f"✓ all_data_styled.json : {len(new_styled)} sheets")

# Vérifier la structure
for sheet_name in new_data:
    print(f"  - {sheet_name} : {len(new_data[sheet_name])} items")
```

**Résultat attendu** :
```
✓ all_data.json : 12 sheets
✓ all_data_styled.json : 12 sheets
  - WeaponPerks : 150 items
  - ArmorSets : 50 items
  ...
```

- [ ] Test 8 réussi
- [ ] Nombre de sheets correct
- [ ] Nombre d'items par sheet correct

---

### Test 9 : Vérification du format styled
```python
# test_styled_format.py
import json

with open("data/styled/WeaponPerks.json", "r") as f:
    styled = json.load(f)

# Vérifier le premier item
first = styled[0]
has_descriptions = "descriptions" in first
has_en = "en" in first.get("descriptions", {})
has_lines = len(first.get("descriptions", {}).get("en", [])) > 0

print(f"✓ descriptions présent : {has_descriptions}")
print(f"✓ descriptions.en présent : {has_en}")
print(f"✓ linesContent présent : {has_lines}")

if has_lines:
    line = first["descriptions"]["en"][0]
    has_linesContent = "linesContent" in line
    print(f"✓ Structure Clarity correcte : {has_linesContent}")
```

**Résultat attendu** :
```
✓ descriptions présent : True
✓ descriptions.en présent : True
✓ linesContent présent : True
✓ Structure Clarity correcte : True
```

- [ ] Test 9 réussi

---

## 🧹 Nettoyage

### Une fois tous les tests validés

- [ ] Supprimer les anciens fichiers :
  ```bash
  rm utils/config.py
  rm utils/fetcher.py
  rm utils/stylizer.py
  rm utils/styles.py
  rm utils/exporter.py
  ```

- [ ] Vérifier qu'aucun import de l'ancien système ne reste :
  ```bash
  grep -r "from utils.config import" .
  grep -r "from utils.fetcher import" .
  grep -r "from utils.stylizer import" .
  grep -r "from utils.styles import" .
  grep -r "from utils.exporter import" .
  ```
  **Résultat attendu** : Aucun résultat (sauf dans les anciens fichiers à supprimer)

- [ ] Commit des changements :
  ```bash
  git add utils/
  git add main.py
  git commit -m "refactor(utils): reorganize into modular structure

  - Split utils into fetch, transform, style, export modules
  - Divide styles.py into patterns, processors, clarity
  - Update main.py with new imports
  - Add comprehensive documentation
  "
  ```

---

## 📝 Notes finales

### Si un test échoue :
1. Vérifier que le fichier existe
2. Vérifier les imports dans `__init__.py`
3. Vérifier que le code a été copié correctement
4. Comparer avec l'ancien fichier

### Points d'attention :
- Les imports relatifs dans les modules (`from utils.style.patterns import ...`)
- La cohérence des noms de fonctions
- Les dépendances entre modules

---

**Date de vérification** : {{ date }}
**Statut final** : [ ] Tous les tests passés ✅