import runpy

scripts = [
    "Process\\updateManifests",
    "Process\\enrichArmorSet",
    "Process\\updateVersion"
]

for script in scripts:
    print(f"\n{'=' * 50}")
    print(f"Exécution de {script}.py...")
    print('=' * 50)

    try:
        runpy.run_path(f"{script}.py")
    except Exception as e:
        print(f"Erreur lors de l'exécution de {script}.py: {e}")