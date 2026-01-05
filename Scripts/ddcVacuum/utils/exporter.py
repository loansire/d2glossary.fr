import json
import webbrowser
import http.server
import socketserver
import threading
from pathlib import Path


def clean_nan_values(obj):
    """Nettoie récursivement les valeurs NaN, None, et chaînes vides"""
    if isinstance(obj, dict):
        return {k: clean_nan_values(v) for k, v in obj.items()
                if v is not None and v != "" and str(v).lower() != "nan"}
    elif isinstance(obj, list):
        return [clean_nan_values(item) for item in obj
                if item is not None and item != "" and str(item).lower() != "nan"]
    else:
        # Si c'est NaN (float) ou la chaîne "NaN", retourner None
        if str(obj).lower() == "nan":
            return None
        return obj


def save_json(data: any, filepath: str) -> None:
    """Sauvegarde des données en JSON en nettoyant les NaN"""
    cleaned_data = clean_nan_values(data)
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(cleaned_data, f, ensure_ascii=False, indent=2)


def start_preview_server(port: int = 8000):
    """Démarre un serveur HTTP local pour éviter les problèmes CORS"""

    class Handler(http.server.SimpleHTTPRequestHandler):
        def log_message(self, format, *args):
            pass  # Supprime les logs du serveur

    with socketserver.TCPServer(("", port), Handler) as httpd:
        print(f"   🌐 Serveur HTTP démarré sur http://localhost:{port}")
        httpd.serve_forever()