# Système de Filtres DDCVacuum

## Vue d'ensemble

Le système de filtres permet d'appliquer des transformations spécifiques à chaque sheet lors de l'import CSV. Les filtres sont modulaires, configurables et réutilisables.

## Architecture

```
filters/
├── __init__.py              # Classe de base BaseFilter
├── config.py                # Configuration des filtres par sheet
├── pipeline.py              # Pipeline d'exécution
├── name_propagation.py      # Filtre: propager Name vide
└── name_source_split.py     # Filtre: séparer Name/Source
```

## Filtres disponibles

### 1. NameSourceSplitFilter

**Objectif**: Sépare le champ `Name` qui contient des retours à la ligne en deux champs distincts.

**Pattern détecté**:
- `name\nsource`
- `name\n\nsource`
- `name\n\n\nsource`

**Configuration**:
```python
{
    "filter": NameSourceSplitFilter,
    "config": {
        "name_field": "Name",      # Champ à analyser
        "source_field": "source"   # Nouveau champ créé
    }
}
```

**Exemple**:
```python
# Avant
{"Name": "Bushido\n\nPinnacle Ops"}

# Après
{"Name": "Bushido", "source": "Pinnacle Ops"}
```

### 2. NamePropagationFilter

**Objectif**: Propage le `Name` de l'enregistrement précédent vers les enregistrements qui ont un `Name` vide.

**Configuration**:
```python
{
    "filter": NamePropagationFilter,
    "config": {
        "name_field": "Name"  # Champ à propager
    }
}
```

**Exemple**:
```python
# Avant
[
    {"Name": "Iron Panoply", "Description": "2 Piece..."},
    {"Name": "", "Description": "4 Piece..."},
    {"Name": "", "Description": "Notes..."}
]

# Après
[
    {"Name": "Iron Panoply", "Description": "2 Piece..."},
    {"Name": "Iron Panoply", "Description": "4 Piece..."},
    {"Name": "Iron Panoply", "Description": "Notes..."}
]
```

## Configuration des filtres

Les filtres sont configurés dans `filters/config.py` via le dictionnaire `SHEET_FILTERS`:

```python
SHEET_FILTERS = {
    "ArmorSets": [
        {
            "filter": NameSourceSplitFilter,
            "config": {...},
            "description": "Sépare le Name et le source"
        },
        {
            "filter": NamePropagationFilter,
            "config": {...},
            "description": "Propage le Name vide"
        }
    ],
    
    "WeaponPerks": [
        {
            "filter": NameSourceSplitFilter,
            "config": {...}
        }
    ]
}
```

**Ordre d'exécution**: Les filtres sont appliqués dans l'ordre de la liste.

## Créer un nouveau filtre

### 1. Créer le fichier du filtre

Créer `filters/mon_filtre.py`:

```python
from filters import BaseFilter

class MonFiltre(BaseFilter):
    """Description du filtre"""
    
    def __init__(self, config: dict = None):
        super().__init__(config)
        # Initialiser les paramètres depuis config
        self.param1 = self.config.get("param1", "default")
    
    def apply(self, records: list[dict]) -> list[dict]:
        """
        Applique le filtre sur tous les records
        """
        processed = []
        
        for record in records:
            processed_record = self.process_record(record)
            processed.append(processed_record)
        
        return processed
    
    def process_record(self, record: dict, context: dict = None) -> dict:
        """
        Traite un enregistrement individuel
        """
        # Logique du filtre
        record = record.copy()
        # ... transformations ...
        return record
```

### 2. Ajouter le filtre à la configuration

Dans `filters/config.py`:

```python
from filters.mon_filtre import MonFiltre

SHEET_FILTERS = {
    "MaSheet": [
        {
            "filter": MonFiltre,
            "config": {
                "param1": "valeur"
            },
            "description": "Description du filtre"
        }
    ]
}
```

### 3. Le filtre sera automatiquement appliqué

Le pipeline détecte et applique les filtres configurés automatiquement lors de l'exécution de `main.py`.

## Exemples d'utilisation

### Appliquer manuellement un filtre

```python
from filters.name_source_split import NameSourceSplitFilter

# Créer une instance
filter_instance = NameSourceSplitFilter({
    "name_field": "Name",
    "source_field": "source"
})

# Appliquer sur des records
records = [{"Name": "Test\n\nSource1"}]
filtered = filter_instance.apply(records)
```

### Utiliser le pipeline

```python
from filters.pipeline import FilterPipeline

# Créer un pipeline pour une sheet
pipeline = FilterPipeline("ArmorSets")

# Voir la description
print(pipeline.describe())

# Appliquer tous les filtres
filtered_records = pipeline.apply(records)
```

### Fonction utilitaire

```python
from filters.pipeline import apply_filters_if_configured

# Applique automatiquement les filtres configurés pour la sheet
filtered = apply_filters_if_configured("ArmorSets", records)
```

## Bonnes pratiques

1. **Immutabilité**: Toujours copier les records avant modification
   ```python
   record = record.copy()
   ```

2. **Gestion d'erreurs**: Utiliser try/except dans les filtres
   ```python
   try:
       # Traitement
   except Exception as e:
       print(f"Erreur: {e}")
       return record  # Retourner l'original
   ```

3. **Configuration**: Utiliser `self.config.get()` avec valeurs par défaut
   ```python
   self.field = self.config.get("field", "Name")
   ```

4. **Documentation**: Documenter clairement le but du filtre et ses paramètres

5. **Tests**: Tester avec des cas limites (valeurs vides, None, NaN)

## Ordre d'application recommandé

Pour une sheet donnée, appliquer les filtres dans cet ordre logique:

1. **Nettoyage/Parse** (ex: NameSourceSplitFilter)
2. **Propagation/Enrichissement** (ex: NamePropagationFilter)
3. **Validation/Vérification**
4. **Transformation finale**

## Debug

Activer les messages de debug dans le pipeline:

```python
# Dans filters/pipeline.py
print(f"      → Filtre {i+1}/{len(self.filters)}: {filter_name}")
```

Chaque filtre affichera son nom lors de l'exécution.