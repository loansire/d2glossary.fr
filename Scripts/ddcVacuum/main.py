import os
import sys
from utils.config import SHEETS, OUTPUT_DIR
from utils.fetcher import fetch_sheet
from utils.stylizer import stylize_records
from utils.exporter import save_json
from filters.pipeline import apply_filters_if_configured, FilterPipeline
from filters.config import has_filters


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
    # Vérification de la configuration
    if not confirm_configuration():
        sys.exit(0)

    # Créer la structure de dossiers
    simple_dir = f"{OUTPUT_DIR}/simple"
    styled_dir = f"{OUTPUT_DIR}/styled"

    os.makedirs(simple_dir, exist_ok=True)
    os.makedirs(styled_dir, exist_ok=True)

    print("🚀 Démarrage de l'export D2 Glossary\n")

    all_raw = {}
    all_styled = {}

    for name, gid in SHEETS.items():
        print(f"📥 Récupération de {name}...")

        try:
            # Récupération des données
            records = fetch_sheet(name, gid)

            # Application des filtres si configurés
            if has_filters(name):
                print(f"   🔧 Application des filtres...")
                records = apply_filters_if_configured(name, records)

            all_raw[name] = records

            # Stylisation
            styled_records = stylize_records(records)
            all_styled[name] = styled_records

            # Sauvegarde dans les sous-dossiers
            save_json(records, f"{simple_dir}/{name}.json")
            save_json(styled_records, f"{styled_dir}/{name}.json")

            print(f"   ✓ {name} ({len(records)} items)")

        except Exception as e:
            print(f"   ✗ Erreur: {e}")
            import traceback
            traceback.print_exc()

    # Sauvegarde des fichiers combinés à la racine du dossier data
    save_json(all_raw, f"{OUTPUT_DIR}/all_data.json")
    save_json(all_styled, f"{OUTPUT_DIR}/all_data_styled.json")

    print(f"\n✅ Export terminé!")
    print(f"   📁 {simple_dir}/ ({len(SHEETS)} fichiers)")
    print(f"   📁 {styled_dir}/ ({len(SHEETS)} fichiers)")
    print(f"   📄 {OUTPUT_DIR}/all_data.json")
    print(f"   📄 {OUTPUT_DIR}/all_data_styled.json")


if __name__ == "__main__":
    main()