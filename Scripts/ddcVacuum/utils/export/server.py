"""
HTTP preview server

Provides a simple HTTP server for local file preview (avoids CORS issues)
"""

import http.server
import socketserver


def start_preview_server(port: int = 8000):
    """
    Démarre un serveur HTTP local pour éviter les problèmes CORS

    Args:
        port: Port d'écoute (défaut: 8000)

    Example:
        >>> start_preview_server(8000)
        🌐 Serveur HTTP démarré sur http://localhost:8000
    """

    class QuietHandler(http.server.SimpleHTTPRequestHandler):
        """Handler HTTP personnalisé sans logs"""

        def log_message(self, format, *args):
            """Supprime les logs du serveur"""
            pass

    # Créer et démarrer le serveur
    with socketserver.TCPServer(("", port), QuietHandler) as httpd:
        print(f"   🌐 Serveur HTTP démarré sur http://localhost:{port}")
        httpd.serve_forever()