"""
Launcher principal: Inicia backend (engine de arbitragem) e frontend (servidor web)
"""

import sys
import os
import threading
import time
import webbrowser

# Adicionar diretório ao path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from backend.arbitrage_engine import ArbitrageEngine
from server import start_server

def run_backend():
    """Roda o engine de arbitragem"""
    print("\n🔧 Iniciando Backend...")
    engine = ArbitrageEngine(output_dir="data")
    engine.start_monitoring()

def run_frontend():
    """Roda o servidor web"""
    time.sleep(2)  # Esperar um pouco antes de iniciar o servidor
    print("\n🌐 Iniciando Frontend...")
    start_server()

def open_browser():
    """Abre o navegador após iniciar os serviços"""
    time.sleep(4)  # Esperar serviços iniciarem
    url = "http://localhost:8000/frontend/index.html"
    print(f"\n🚀 Abrindo navegador em: {url}")
    try:
        webbrowser.open(url)
    except Exception as e:
        print(f"⚠️  Não foi possível abrir o navegador automaticamente: {e}")
        print(f"   Abra manualmente: {url}")

def main():
    """Função principal que coordena backend e frontend"""
    print("=" * 70)
    print("🚀 CRYPTO ARBITRAGE MONITOR - SISTEMA COMPLETO")
    print("=" * 70)
    print("📦 Componentes:")
    print("   1. Backend: Engine de arbitragem com dados reais")
    print("   2. Frontend: Interface web interativa")
    print("   3. Servidor: HTTP server na porta 8000")
    print("=" * 70)
    print()

    # Criar diretório de dados se não existir
    os.makedirs("data", exist_ok=True)

    try:
        # Iniciar backend em thread separada
        backend_thread = threading.Thread(target=run_backend, daemon=True)
        backend_thread.start()

        # Esperar um pouco para o backend fazer a primeira coleta
        print("⏳ Aguardando primeira coleta de dados...")
        time.sleep(10)

        # Abrir navegador em thread separada
        browser_thread = threading.Thread(target=open_browser, daemon=True)
        browser_thread.start()

        # Iniciar frontend (servidor web) na thread principal
        run_frontend()

    except KeyboardInterrupt:
        print("\n\n🛑 Encerrando sistema...")
        print("✅ Sistema encerrado com sucesso!")
        sys.exit(0)

if __name__ == "__main__":
    # Verificar dependências
    try:
        import numpy
        import requests
    except ImportError as e:
        print("❌ ERRO: Dependências não instaladas")
        print(f"   {e}")
        print("\n💡 Execute: pip install numpy requests")
        sys.exit(1)

    main()
