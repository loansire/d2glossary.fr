"""
DDCVacuum - Destiny 2 Data Compendium Vacuum
Main entry point for exporting Google Sheets data to JSON

Pipeline:
    Fetch → Filter → Hash Recovery → Transform → Export
"""

import os
import sys

# Utils imports - New modular structure
from utils import (
    # Configuration
    SHEETS, OUTPUT_DIR,
    # Fetch
    fetch_sheet,
    # Transform
    stylize_records,
    # Export
    save_json
)

# Filters imports
from filters.pipeline import apply_filters_if_configured
from filters.config import has_filters

# Hash Recovery imports
from utils.hashRecov import HashEnricher, HASH_MAPPINGS


def confirm_configuration():
    """Demande confirmation de la configuration du panel ddcVacuum"""

    print("=" * 70)
    print("🔧 Configuration requise")
    print("\nAvant de lancer l'export, assurez-vous d'avoir configuré le panel :")
    print("\n📋 Lien du ddcVacuum Panel :")
    print("https://docs.google.com/spreadsheets/d/1tfa3mEwTWLrPUEw2p9aRKWUH37quVgpkyVisB6E1DZU/edit?usp=sharing")
    print("\n📋 Lien du DestinyDataCompendium :")
    print("https://docs.google.com/spreadsheets/d/1WaxvbLx7UoSZaBqdFr1u32F2uWVLo-CJunJB4nlGUE4/edit?usp=sharing")
    print("\n" + "=" * 70)

    response = input("\nAvez-vous configuré le ddcVacuum panel pour cette version ? (y/n) : ").strip().lower()

    if response in ['oui', 'o', 'yes', 'y']:
        print("\n✅ Configuration confirmée. Démarrage de l'export...\n")
        return True
    else:
        print("\n❌ Veuillez d'abord configurer le panel avant de lancer l'export.")
        print("Programme arrêté.\n")
        return False


def main():
    """
    Main execution pipeline:
    1. Confirm configuration
    2. Create output directories
    3. For each sheet:
        - Fetch data from Google Sheets
        - Apply filters if configured
        - Stylize records (add DDCVacuum format)
        - Export to JSON (simple and styled)
    4. Hash Recovery (après filtres, avant stylisation finale):
        - Enrichir les données avec les hash depuis d2glossary
        - Sauvegarder dans hashrecov/
    5. Export combined files
    """
    # Vérification de la configuration
    if not confirm_configuration():
        sys.exit(0)

    # Créer la structure de dossiers
    simple_dir = f"{OUTPUT_DIR}/simple"
    styled_dir = f"{OUTPUT_DIR}/styled"
    hashrecov_dir = f"{OUTPUT_DIR}/hashrecov"

    os.makedirs(simple_dir, exist_ok=True)
    os.makedirs(styled_dir, exist_ok=True)
    os.makedirs(hashrecov_dir, exist_ok=True)

    print("🚀 Démarrage de l'export D2 Glossary\n")

    all_raw = {}
    all_styled = {}
    all_enriched = {}

    # Initialiser le HashEnricher
    hash_enricher = HashEnricher()

    for name, gid in SHEETS.items():
        print(f"📥 Récupération de {name}...")

        try:
            # 1. Récupération des données
            records = fetch_sheet(name, gid)

            # 2. Application des filtres si configurés
            if has_filters(name):
                print(f"   🔧 Application des filtres...")
                records = apply_filters_if_configured(name, records)

            # Sauvegarder version simple (après filtres)
            all_raw[name] = records
            save_json(records, f"{simple_dir}/{name}.json")

            # 3. Hash Recovery (si configuré pour cette sheet)
            enriched_records = records  # Par défaut, utiliser les records filtrés

            if name in HASH_MAPPINGS:
                print(f"   🔑 Enrichissement avec hash d2glossary...")

                try:
                    # Sauvegarder temporairement dans simple/ pour que HashEnricher puisse le lire
                    # (car il lit depuis ddcvacuum_base = "data/simple")
                    temp_path = f"{simple_dir}/{name}.json"
                    save_json(records, temp_path)

                    # Enrichir avec les hash
                    result = hash_enricher.enrich_sheet(name)
                    enriched_records = result["enriched_records"]

                    # Sauvegarder version enrichie
                    save_json(enriched_records, f"{hashrecov_dir}/{name}.json")
                    all_enriched[name] = enriched_records

                    # Afficher les stats
                    stats = result["stats"]
                    print(f"      ✓ {stats['enriched_records']}/{stats['total_records']} enrichis")

                    if stats['no_match'] > 0:
                        print(f"      ⚠️  {stats['no_match']} sans match:")
                        for detail in stats['details']:
                            if detail['type'] == 'no_match':
                                print(f"         - {detail['name']}")

                    if stats['multiple_matches'] > 0:
                        print(f"      🔁 {stats['multiple_matches']} matches multiples")

                except Exception as e:
                    print(f"      ⚠️  Erreur hash recovery: {e}")
                    # Continuer avec les records non-enrichis
                    enriched_records = records

            # 4. Stylisation (sur les records enrichis si disponibles)
            print(f"   🎨 Stylisation...")
            styled_records = stylize_records(enriched_records)
            all_styled[name] = styled_records
            save_json(styled_records, f"{styled_dir}/{name}.json")

            print(f"   ✓ {name} ({len(records)} items)")

        except Exception as e:
            print(f"   ✗ Erreur: {e}")
            import traceback
            traceback.print_exc()

    # Sauvegarde des fichiers combinés à la racine du dossier data
    save_json(all_raw, f"{OUTPUT_DIR}/all_data.json")
    save_json(all_styled, f"{OUTPUT_DIR}/all_data_styled.json")

    if all_enriched:
        save_json(all_enriched, f"{OUTPUT_DIR}/all_data_enriched.json")

    print(f"\n✅ Export terminé!")
    print(f"   📁 {simple_dir}/ ({len(SHEETS)} fichiers)")
    print(f"   📁 {styled_dir}/ ({len(SHEETS)} fichiers)")
    if all_enriched:
        print(f"   📁 {hashrecov_dir}/ ({len(all_enriched)} fichiers enrichis)")
    print(f"   📄 {OUTPUT_DIR}/all_data.json")
    print(f"   📄 {OUTPUT_DIR}/all_data_styled.json")
    if all_enriched:
        print(f"   📄 {OUTPUT_DIR}/all_data_enriched.json")


if __name__ == "__main__":
    main()