"""
Hash Enricher - Main module for enriching ddcVacuum data with d2glossary hashes
"""

import json
import os
from typing import Dict, List, Any
from .config import (
    D2GLOSSARY_BASE,
    DDCVACUUM_BASE,
    HASH_MAPPINGS,
    get_nested_value
)
from .matcher import find_hash_matches, enrich_record_with_hashes


class HashEnricher:
    """
    Enrichit les données ddcVacuum avec les hash depuis d2glossary.

    Usage:
        enricher = HashEnricher()
        enricher.enrich_sheet("ArmorSets")
        enricher.save_enriched("ArmorSets", "data/simple_enriched")
    """

    def __init__(self, d2glossary_base: str = D2GLOSSARY_BASE, ddcvacuum_base: str = DDCVACUUM_BASE):
        """
        Initialise l'enricher.

        Args:
            d2glossary_base: Chemin vers le dossier d2glossary/data/en
            ddcvacuum_base: Chemin vers le dossier ddcVacuum/data/simple
        """
        self.d2glossary_base = d2glossary_base
        self.ddcvacuum_base = ddcvacuum_base
        self.glossary_cache = {}
        self.enriched_data = {}
        self.stats = {}

    def load_glossary_data(self, source_file: str) -> Dict[str, Any]:
        """
        Charge un fichier JSON depuis d2glossary (avec cache).

        Args:
            source_file: Nom du fichier (ex: "set_armor_definitions_enriched.json")

        Returns:
            Données JSON chargées
        """
        if source_file in self.glossary_cache:
            return self.glossary_cache[source_file]

        filepath = os.path.join(self.d2glossary_base, source_file)

        if not os.path.exists(filepath):
            raise FileNotFoundError(f"d2glossary file not found: {filepath}")

        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)
            self.glossary_cache[source_file] = data
            return data

    def load_vacuum_data(self, sheet_name: str) -> List[Dict[str, Any]]:
        """
        Charge un fichier JSON depuis ddcVacuum.

        Args:
            sheet_name: Nom de la sheet (ex: "ArmorSets")

        Returns:
            Liste des records
        """
        filepath = os.path.join(self.ddcvacuum_base, f"{sheet_name}.json")

        if not os.path.exists(filepath):
            raise FileNotFoundError(f"ddcVacuum file not found: {filepath}")

        with open(filepath, 'r', encoding='utf-8') as f:
            return json.load(f)

    def enrich_sheet(self, sheet_name: str) -> Dict[str, Any]:
        """
        Enrichit une sheet ddcVacuum avec les hash depuis d2glossary.

        Args:
            sheet_name: Nom de la sheet à enrichir (ex: "ArmorSets")

        Returns:
            Dictionnaire avec statistiques et données enrichies

        Example:
            >>> enricher = HashEnricher()
            >>> result = enricher.enrich_sheet("ArmorSets")
            >>> print(result["stats"])
            {
                "total_records": 50,
                "enriched_records": 48,
                "no_match": 2,
                "multiple_matches": 3
            }
        """
        # Vérifier que le mapping existe
        if sheet_name not in HASH_MAPPINGS:
            raise ValueError(f"No hash mapping configured for sheet: {sheet_name}")

        mapping = HASH_MAPPINGS[sheet_name]

        # Charger les données
        print(f"📥 Chargement de {sheet_name}...")
        vacuum_records = self.load_vacuum_data(sheet_name)

        print(f"📥 Chargement de {mapping['source']}...")
        glossary_data = self.load_glossary_data(mapping['source'])

        # Statistiques
        stats = {
            "total_records": len(vacuum_records),
            "enriched_records": 0,
            "no_match": 0,
            "multiple_matches": 0,
            "details": []
        }

        enriched_records = []

        # Parcourir chaque record
        for record in vacuum_records:
            name = record.get("Name")

            if not name:
                print(f"⚠️  Record sans nom ignoré: {record}")
                continue

            # Rechercher les hash correspondants
            matches = find_hash_matches(
                name,
                glossary_data,
                mapping["name_path"],
                mapping["hash_path"],
                mapping.get("array_path")
            )

            # Enrichir le record
            enriched = enrich_record_with_hashes(record, matches)
            enriched_records.extend(enriched)

            # Mettre à jour les stats
            if matches:
                stats["enriched_records"] += len(enriched)
                if len(matches) > 1:
                    stats["multiple_matches"] += 1
                    stats["details"].append({
                        "name": name,
                        "type": "multiple_matches",
                        "count": len(matches),
                        "hashes": [m["hash"] for m in matches]
                    })
            else:
                stats["no_match"] += 1
                stats["details"].append({
                    "name": name,
                    "type": "no_match"
                })

        # Sauvegarder les résultats
        self.enriched_data[sheet_name] = enriched_records
        self.stats[sheet_name] = stats

        return {
            "sheet_name": sheet_name,
            "stats": stats,
            "enriched_records": enriched_records
        }

    def save_enriched(self, sheet_name: str, output_dir: str = "data/simple_enriched"):
        """
        Sauvegarde les données enrichies dans un fichier JSON.

        Args:
            sheet_name: Nom de la sheet
            output_dir: Dossier de sortie
        """
        if sheet_name not in self.enriched_data:
            raise ValueError(f"No enriched data for sheet: {sheet_name}")

        os.makedirs(output_dir, exist_ok=True)

        filepath = os.path.join(output_dir, f"{sheet_name}.json")

        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(self.enriched_data[sheet_name], f, ensure_ascii=False, indent=2)

        print(f"💾 Sauvegardé: {filepath}")

    def print_report(self, sheet_name: str):
        """
        Affiche un rapport détaillé sur l'enrichissement.

        Args:
            sheet_name: Nom de la sheet
        """
        if sheet_name not in self.stats:
            raise ValueError(f"No stats for sheet: {sheet_name}")

        stats = self.stats[sheet_name]

        print("\n" + "=" * 70)
        print(f"📊 Rapport d'enrichissement - {sheet_name}")
        print("=" * 70)
        print(f"Total records:        {stats['total_records']}")
        print(f"Records enrichis:     {stats['enriched_records']}")
        print(f"Sans match:           {stats['no_match']}")
        print(f"Matches multiples:    {stats['multiple_matches']}")

        if stats['details']:
            print("\n📋 Détails:")
            for detail in stats['details']:
                if detail['type'] == 'no_match':
                    print(f"  ⚠️  Aucun match: {detail['name']}")
                elif detail['type'] == 'multiple_matches':
                    print(f"  🔁 {detail['count']} matches: {detail['name']}")
                    print(f"      Hash: {detail['hashes']}")

        print("=" * 70 + "\n")