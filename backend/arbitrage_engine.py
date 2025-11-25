"""
Backend: Engine de arbitragem que processa dados reais e detecta oportunidades
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from a import CryptoArbitrageMonitor
from backend.crypto_data_fetcher import RealTimeDataManager
import json
import time
from datetime import datetime
from typing import List, Dict
import threading

class ArbitrageEngine:
    """Engine principal que coordena coleta de dados e detecção de arbitragem"""

    def __init__(self, output_dir: str = "data"):
        self.monitor = CryptoArbitrageMonitor()
        self.data_manager = RealTimeDataManager(update_interval=30)
        self.output_dir = output_dir
        self.opportunities_history = []
        self.is_running = False

        # Criar diretório de saída
        os.makedirs(output_dir, exist_ok=True)

        # Registrar callback para quando dados forem atualizados
        self.data_manager.add_callback(self._on_data_updated)

    def _on_data_updated(self, rates, summary):
        """Callback chamado quando dados são atualizados"""
        if self.is_running:
            self.process_arbitrage(rates, summary)

    def process_arbitrage(self, rates, summary):
        """Processa detecção de arbitragem com taxas atualizadas"""
        print(f"\n{'='*60}")
        print(f"🔍 ANÁLISE DE ARBITRAGEM - {datetime.now().strftime('%H:%M:%S')}")
        print(f"{'='*60}")

        # Atualizar monitor com novas taxas
        self.monitor.update_rates(rates)

        # Obter estatísticas
        stats = self.monitor.get_arbitrage_statistics()
        print(f"📊 Mercado: {stats['total_currencies']} moedas, "
              f"{stats['available_pairs']} pares ({stats['coverage_percent']:.1f}% cobertura)")

        # Buscar oportunidades usando método otimizado
        start_time = time.time()
        opportunities = self.monitor.optimized_bellman_ford()
        detection_time = time.time() - start_time

        print(f"⚡ Detecção: {detection_time:.4f}s")

        # Também buscar triangulares para comparação se o grafo for pequeno
        if stats['total_currencies'] < 15:
            triangle_opps = self.monitor.find_arbitrage_opportunities()
            print(f"🔺 Triangulares: {len(triangle_opps)} encontradas")

            # Combinar oportunidades (remover duplicatas)
            all_opps = self._merge_opportunities(opportunities, triangle_opps)
            opportunities = all_opps

        # Filtrar e ordenar
        opportunities = [opp for opp in opportunities if opp['profit_percent'] > 0.1]
        opportunities = sorted(opportunities, key=lambda x: x['profit_percent'], reverse=True)

        # Exibir resultados
        if opportunities:
            print(f"\n💰 {len(opportunities)} OPORTUNIDADES ENCONTRADAS:")
            for i, opp in enumerate(opportunities[:5]):  # Top 5
                path_str = " → ".join(opp['path'])
                print(f"\n   #{i+1} Lucro: {opp['profit_percent']:.4f}%")
                print(f"       Rota: {path_str}")
                print(f"       Produto: {opp['product']:.8f}")
        else:
            print("\n📭 Nenhuma oportunidade de arbitragem encontrada")
            print("   (Mercado eficiente no momento)")

        # Salvar resultados
        self._save_results(opportunities, stats, summary, detection_time)

        # Adicionar ao histórico
        self.opportunities_history.append({
            'timestamp': datetime.now().isoformat(),
            'count': len(opportunities),
            'top_profit': opportunities[0]['profit_percent'] if opportunities else 0
        })

    def _merge_opportunities(self, opps1: List[Dict], opps2: List[Dict]) -> List[Dict]:
        """Mescla e remove oportunidades duplicadas"""
        seen_paths = set()
        merged = []

        for opp in opps1 + opps2:
            # Criar assinatura do caminho
            path_sig = tuple(sorted(opp['path']))
            if path_sig not in seen_paths:
                seen_paths.add(path_sig)
                merged.append(opp)

        return merged

    def _save_results(self, opportunities, stats, summary, detection_time):
        """Salva resultados em arquivo JSON para o frontend"""
        results = {
            'timestamp': datetime.now().isoformat(),
            'detection_time_seconds': detection_time,
            'market': {
                'currencies': stats['total_currencies'],
                'pairs': stats['available_pairs'],
                'coverage_percent': stats['coverage_percent'],
                'all_currencies': summary.get('currencies', [])
            },
            'opportunities': [
                {
                    'path': opp['path'],
                    'profit_percent': round(opp['profit_percent'], 4),
                    'product': round(opp['product'], 8),
                    'path_length': len(opp['path']) - 1
                }
                for opp in opportunities[:20]  # Top 20
            ],
            'statistics': {
                'total_found': len(opportunities),
                'max_profit': opportunities[0]['profit_percent'] if opportunities else 0,
                'avg_profit': sum(o['profit_percent'] for o in opportunities) / len(opportunities) if opportunities else 0
            }
        }

        # Salvar arquivo principal
        output_path = os.path.join(self.output_dir, "arbitrage_results.json")
        with open(output_path, 'w') as f:
            json.dump(results, f, indent=2)

        # Salvar histórico
        history_path = os.path.join(self.output_dir, "history.json")
        with open(history_path, 'w') as f:
            json.dump(self.opportunities_history[-100:], f, indent=2)  # Últimos 100

    def start_monitoring(self):
        """Inicia monitoramento contínuo"""
        print("\n" + "="*60)
        print("🚀 INICIANDO ENGINE DE ARBITRAGEM")
        print("="*60)
        print("📡 Conectando a exchanges...")
        print("🔄 Atualizações automáticas a cada 30 segundos")
        print("💡 Pressione Ctrl+C para parar")
        print("="*60)

        self.is_running = True

        # Fazer primeira atualização imediatamente
        self.data_manager.update_data()
        rates, summary = self.data_manager.get_current_data()
        self.process_arbitrage(rates, summary)

        # Iniciar atualizações automáticas
        self.data_manager.start()

        try:
            # Manter rodando
            while self.is_running:
                time.sleep(1)

        except KeyboardInterrupt:
            print("\n\n🛑 Parando engine...")
            self.stop_monitoring()

    def stop_monitoring(self):
        """Para monitoramento"""
        self.is_running = False
        self.data_manager.stop()
        print("✅ Engine parada")

        # Estatísticas finais
        if self.opportunities_history:
            total_checks = len(self.opportunities_history)
            total_opps = sum(h['count'] for h in self.opportunities_history)
            max_profit = max(h['top_profit'] for h in self.opportunities_history)

            print(f"\n📊 ESTATÍSTICAS FINAIS:")
            print(f"   Verificações: {total_checks}")
            print(f"   Oportunidades totais: {total_opps}")
            print(f"   Maior lucro: {max_profit:.4f}%")


def main():
    """Função principal para executar o engine"""
    engine = ArbitrageEngine(output_dir="data")
    engine.start_monitoring()


if __name__ == "__main__":
    main()
