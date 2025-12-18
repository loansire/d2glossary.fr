import os
from utils.config import SHEETS, OUTPUT_DIR
from utils.fetcher import fetch_sheet
from utils.stylizer import stylize_records
from utils.exporter import save_json, save_css, generate_html


def main():
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    print("🚀 Démarrage de l'export D2 Glossary\n")

    all_raw = {}
    all_styled = {}

    for name, gid in SHEETS.items():
        print(f"📥 Récupération de {name}...")

        try:
            # Fetch
            records = fetch_sheet(name, gid)
            all_raw[name] = records

            # Stylize
            styled_records = stylize_records(records)
            all_styled[name] = styled_records

            # Export individuel
            save_json(records, f"{OUTPUT_DIR}/{name}.json")
            save_json(styled_records, f"{OUTPUT_DIR}/{name}_styled.json")

            print(f"   ✓ {name} ({len(records)} items)")

        except Exception as e:
            print(f"   ✗ Erreur: {e}")

    # Exports globaux
    save_json(all_raw, f"{OUTPUT_DIR}/all_data.json")
    save_json(all_styled, f"{OUTPUT_DIR}/all_data_styled.json")
    save_css(f"{OUTPUT_DIR}/styles.css")
    generate_html(all_styled, f"{OUTPUT_DIR}/preview.html")

    print(f"\n✅ Export terminé!")
    print(f"   📁 {OUTPUT_DIR}/all_data.json")
    print(f"   📁 {OUTPUT_DIR}/all_data_styled.json")
    print(f"   📁 {OUTPUT_DIR}/styles.css")
    print(f"   📁 {OUTPUT_DIR}/preview.html")


if __name__ == "__main__":
    main()