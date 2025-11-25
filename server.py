"""
Servidor web simples para servir o frontend e permitir leitura dos dados JSON
"""

import http.server
import socketserver
import os
import json
from urllib.parse import urlparse, parse_qs
import threading
import time

PORT = 8000

class CORSHTTPRequestHandler(http.server.SimpleHTTPRequestHandler):
    """Handler HTTP com suporte a CORS"""

    def end_headers(self):
        # Adicionar headers CORS
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.send_header('Cache-Control', 'no-store, no-cache, must-revalidate')
        super().end_headers()

    def do_OPTIONS(self):
        self.send_response(200)
        self.end_headers()

    def do_GET(self):
        """Servir arquivos com suporte especial para dados JSON"""
        parsed_path = urlparse(self.path)
        path = parsed_path.path

        # Redirecionar / para /frontend/index.html
        if path == '/':
            path = '/frontend/index.html'

        # Servir arquivos normalmente
        self.path = path
        return super().do_GET()

    def log_message(self, format, *args):
        """Log personalizado"""
        # Mostrar apenas requisições importantes
        # Verificar se args[0] é uma string antes de tentar usar 'in'
        if args and isinstance(args[0], str):
            if any(x in args[0] for x in ['.css', '.js', '.json']):
                print(f"[SERVER] {args[0]}")
        # Silenciar outros logs (erros, etc.)


def start_server():
    """Inicia servidor web"""
    # Mudar para diretório raiz do projeto
    os.chdir(os.path.dirname(os.path.abspath(__file__)))

    with socketserver.TCPServer(("", PORT), CORSHTTPRequestHandler) as httpd:
        print("=" * 60)
        print("🌐 SERVIDOR WEB INICIADO")
        print("=" * 60)
        print(f"📡 URL: http://localhost:{PORT}")
        print(f"📁 Servindo arquivos de: {os.getcwd()}")
        print("💡 Pressione Ctrl+C para parar")
        print("=" * 60)
        print()

        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\n🛑 Servidor parado")


def main():
    """Função principal"""
    start_server()


if __name__ == "__main__":
    main()
