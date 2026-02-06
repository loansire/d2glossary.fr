"""
main.py - Script principal pour la mise à jour du D2Glossary (multilingue)
Orchestre l'exécution de tous les processus de mise à jour des données
"""
import sys
from pathlib import Path

# Ajouter le dossier courant au path pour les imports
sys.path.insert(0, str(Path(__file__).parent))

from Process.updateManifests import update_manifests
from Process.enrichArmorSet import enrich_armor_sets
from Process.updateVersion import update_version
from Utils.paths import SUPPORTED_LANGUAGES
from Process.enrichSubclass import enrich_subclasses


def print_header(title):
    """Affiche un en-tête formaté"""
    print("\n")
    print("=" * 80)
    print(f"  {title}")
    print("=" * 80)


def print_step(step_num, total_steps, description):
    """Affiche l'étape en cours"""
    print(f"\n[ÉTAPE {step_num}/{total_steps}] {description}")


def main():
    """Point d'entrée principal du script"""
    import argparse

    parser = argparse.ArgumentParser(
        description='Mise à jour des données D2Glossary',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Exemples d'utilisation:
  python main.py                    # Toutes les langues
  python main.py --lang fr          # Français seulement
  python main.py --lang fr en       # Français et anglais
        """
    )
    parser.add_argument(
        '--lang',
        nargs='+',
        choices=SUPPORTED_LANGUAGES,
        help='Langues à traiter (par défaut: toutes)'
    )

    args = parser.parse_args()
    languages = args.lang if args.lang else SUPPORTED_LANGUAGES

    print_header(f"🎮 D2GLOSSARY - MISE À JOUR DES DONNÉES")
    print(f"\n🌐 Langues sélectionnées: {', '.join(lang.upper() for lang in languages)}")

    total_steps = 3
    current_step = 0
    success = True

    # === ÉTAPE 1 : Téléchargement des manifests ===
    current_step += 1
    print_step(current_step, total_steps, "Téléchargement des manifests Bungie")

    try:
        if not update_manifests(languages):
            print("\n❌ Échec du téléchargement des manifests")
            success = False
    except Exception as e:
        print(f"\n❌ Erreur lors du téléchargement des manifests: {e}")
        success = False

    if not success:
        print_header("❌ ÉCHEC DE LA MISE À JOUR")
        return False

    # === ÉTAPE 2 : Enrichissement des données ===
    current_step += 1
    print_step(current_step, total_steps, "Enrichissement des données")

    try:
        if not enrich_armor_sets():
            print("\n❌ Échec de l'enrichissement des sets/artefacts")
            success = False

        # Enrichir les subclass
        if success and not enrich_subclasses():
            print("\n❌ Échec de l'enrichissement des subclass")
            success = False

    except Exception as e:
        print(f"\n❌ Erreur lors de l'enrichissement: {e}")
        success = False

    # === ÉTAPE 3 : Mise à jour de la version ===
    current_step += 1
    print_step(current_step, total_steps, "Mise à jour de la version")

    try:
        if not update_version():
            print("\n❌ Échec de la mise à jour de la version")
            success = False
    except Exception as e:
        print(f"\n❌ Erreur lors de la mise à jour de la version: {e}")
        success = False

    # === RÉSULTAT FINAL ===
    if success:
        print_header("✅ MISE À JOUR TERMINÉE AVEC SUCCÈS")
        print("\n📊 Résumé:")
        print("   ✅ Manifests téléchargés et nettoyés")
        print("   ✅ Données enrichies (sets d'armure et artefacts)")
        print("   ✅ Données enrichies (sets d'armure, artefacts et subclass)")
        print("   ✅ Version mise à jour")
        print(f"\n🌐 Langues traitées: {', '.join(lang.upper() for lang in languages)}")
        print(f"\n💡 Les données sont maintenant disponibles dans:")
        for lang in languages:
            print(f"   - data/{lang}/")
    else:
        print_header("❌ ÉCHEC DE LA MISE À JOUR")
        print("\n⚠️  Certaines étapes ont échoué. Consultez les messages d'erreur ci-dessus.")

    print("\n")
    return success


if __name__ == "__main__":
    try:
        success = main()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\n⚠️  Interruption par l'utilisateur")
        sys.exit(130)
    except Exception as e:
        print(f"\n\n❌ Erreur fatale: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)