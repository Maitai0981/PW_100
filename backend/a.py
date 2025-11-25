import math
import random
from typing import List, Tuple, Dict
import time

class CryptoArbitrageMonitor:
    def __init__(self):
        self.currencies = []
        self.currency_idx = {}
        self.rates = {}
        
    def update_rates(self, rates: List[Tuple[str, str, float]]):
        """Atualiza as taxas de câmbio e constrói a matriz de taxas"""
        # Coletar todas as moedas únicas
        currencies = set()
        for from_curr, to_curr, rate in rates:
            currencies.add(from_curr)
            currencies.add(to_curr)
        
        self.currencies = sorted(list(currencies))
        self.currency_idx = {curr: i for i, curr in enumerate(self.currencies)}
        
        # Inicializar matriz de taxas com 0 (sem conversão)
        n = len(self.currencies)
        self.rates = [[0.0] * n for _ in range(n)]
        
        # Preencher a matriz com as taxas conhecidas
        for from_curr, to_curr, rate in rates:
            i = self.currency_idx[from_curr]
            j = self.currency_idx[to_curr]
            self.rates[i][j] = rate
            
        # Preencher diagonal (conversão para mesma moeda)
        for i in range(n):
            self.rates[i][i] = 1.0
            
    def find_arbitrage_opportunities(self) -> List[List[str]]:
        """Encontra todas as oportunidades de arbitragem triangular"""
        n = len(self.currencies)
        opportunities = []
        
        # Verificar todos os trios possíveis
        for i in range(n):
            for j in range(n):
                for k in range(n):
                    if i == j or j == k or i == k:
                        continue
                    
                    # Calcular o produto das taxas no triângulo
                    rate1 = self.rates[i][j]  # i -> j
                    rate2 = self.rates[j][k]  # j -> k  
                    rate3 = self.rates[k][i]  # k -> i
                    
                    if rate1 > 0 and rate2 > 0 and rate3 > 0:
                        product = rate1 * rate2 * rate3
                        
                        # Se o produto > 1, há oportunidade de arbitragem
                        if product > 1.001:  # 0.1% de margem para custos
                            profit_percent = (product - 1) * 100
                            path = [
                                self.currencies[i],
                                self.currencies[j], 
                                self.currencies[k],
                                self.currencies[i]
                            ]
                            opportunities.append({
                                'path': path,
                                'profit_percent': profit_percent,
                                'rates': [rate1, rate2, rate3],
                                'product': product
                            })
        
        return sorted(opportunities, key=lambda x: x['profit_percent'], reverse=True)
    
    def bellman_ford_arbitrage(self) -> List[Dict]:
        """Versão aprimorada usando Bellman-Ford para detectar ciclos negativos"""
        n = len(self.currencies)
        dist = [0.0] * n
        predec = [-1] * n
        
        # Inicializar distâncias
        for i in range(n):
            dist[i] = 0.0 if i == 0 else float('inf')
        
        # Aplicar Bellman-Ford com transformação logarítmica
        edges = []
        for i in range(n):
            for j in range(n):
                if i != j and self.rates[i][j] > 0:
                    # Transformação: maximizar produto = minimizar soma de -log(rate)
                    weight = -math.log(self.rates[i][j])
                    edges.append((i, j, weight))
        
        # Relaxamento das arestas
        for _ in range(n - 1):
            for u, v, w in edges:
                if dist[u] != float('inf') and dist[u] + w < dist[v]:
                    dist[v] = dist[u] + w
                    predec[v] = u
        
        # Detectar ciclos negativos (oportunidades de arbitragem)
        arbitrage_cycles = []
        for u, v, w in edges:
            if dist[u] != float('inf') and dist[u] + w < dist[v]:
                # Encontrou ciclo negativo - reconstruir o ciclo
                cycle = self._reconstruct_cycle(v, predec)
                if cycle and len(cycle) > 2:
                    profit = self._calculate_cycle_profit(cycle)
                    if profit > 1.001:
                        arbitrage_cycles.append({
                            'path': [self.currencies[i] for i in cycle],
                            'profit_percent': (profit - 1) * 100,
                            'product': profit
                        })
        
        return arbitrage_cycles
    
    def _reconstruct_cycle(self, start: int, predec: List[int]) -> List[int]:
        """Reconstrói o ciclo a partir dos predecessores"""
        # Encontrar um nó no ciclo
        visited = set()
        node = start
        while node not in visited and node != -1:
            visited.add(node)
            node = predec[node]
        
        if node == -1:
            return []
        
        # Reconstruir o ciclo
        cycle = []
        current = node
        while True:
            cycle.append(current)
            current = predec[current]
            if current == node and len(cycle) > 1:
                break
            if len(cycle) > len(self.currencies):
                return []  # Ciclo muito longo - provavelmente erro
        
        return cycle[::-1]  # Inverter para ordem correta
    
    def _calculate_cycle_profit(self, cycle: List[int]) -> float:
        """Calcula o lucro de um ciclo de arbitragem"""
        profit = 1.0
        for i in range(len(cycle)):
            from_idx = cycle[i]
            to_idx = cycle[(i + 1) % len(cycle)]
            profit *= self.rates[from_idx][to_idx]
        return profit

    def get_arbitrage_statistics(self) -> Dict:
        """Retorna estatísticas sobre o estado atual do mercado"""
        n = len(self.currencies)
        total_pairs = n * (n - 1)

        # Contar pares disponíveis (com taxa > 0)
        available_pairs = 0
        for i in range(n):
            for j in range(n):
                if i != j and self.rates[i][j] > 0:
                    available_pairs += 1

        return {
            'total_currencies': n,
            'total_possible_pairs': total_pairs,
            'available_pairs': available_pairs,
            'coverage_percent': (available_pairs / total_pairs * 100) if total_pairs > 0 else 0
        }

    def optimized_bellman_ford(self) -> List[Dict]:
        """Alias para bellman_ford_arbitrage - versão otimizada"""
        return self.bellman_ford_arbitrage()

def simulate_market_data() -> List[Tuple[str, str, float]]:
    """Simula dados de mercado em tempo real com oportunidades de arbitragem"""
    # Taxas base (sem arbitragem)
    base_rates = [
        ("BTC", "USD", 50000.0),
        ("USD", "EUR", 0.91),
        ("EUR", "BTC", 0.000022),
        ("BTC", "ETH", 15.0),
        ("ETH", "USD", 3300.0),
        ("USD", "GBP", 0.79),
        ("GBP", "BTC", 0.000025),
    ]
    
    # Adicionar algumas oportunidades de arbitragem
    arbitrage_rates = [
        ("USD", "JPY", 110.0),
        ("JPY", "EUR", 0.0075),  # Esta taxa cria arbitragem
        ("EUR", "USD", 1.10),
    ]

    # Misturar com algumas taxas variáveis
    all_rates = base_rates + arbitrage_rates
    
    # Adicionar pequenas variações para simular mercado real
    varied_rates = []
    for from_curr, to_curr, rate in all_rates:
        # Variação de ±0.1%
        variation = random.uniform(0.999, 1.001)
        varied_rates.append((from_curr, to_curr, rate * variation))
    
    return varied_rates

def main():
    """Função principal do monitor de arbitragem"""
    monitor = CryptoArbitrageMonitor()
    
    print("🚀 Iniciando Monitor de Arbitragem de Criptoativos")
    print("=" * 60)
    
    try:
        while True:
            # Simular atualização de dados de mercado
            market_rates = simulate_market_data()
            monitor.update_rates(market_rates)
            
            print(f"\n📊 Verificação em {time.strftime('%H:%M:%S')}")
            print("-" * 40)
            
            # Método 1: Busca por triângulos
            opportunities = monitor.find_arbitrage_opportunities()
            
            if opportunities:
                print("💰 OPORTUNIDADES DE ARBITRAGEM ENCONTRADAS:")
                for opp in opportunities[:3]:  # Mostrar até 3 melhores
                    print(f"   ↪ {opp['path'][0]} → {opp['path'][1]} → {opp['path'][2]} → {opp['path'][3]}")
                    print(f"     Lucro: {opp['profit_percent']:.4f}%")
                    print(f"     Taxas: {opp['rates'][0]:.6f} × {opp['rates'][1]:.6f} × {opp['rates'][2]:.6f} = {opp['product']:.6f}")
                    print()
            else:
                print("   📭 Nenhuma oportunidade triangular encontrada")
            
            # Método 2: Bellman-Ford (ciclos mais complexos)
            bellman_opportunities = monitor.bellman_ford_arbitrage()
            
            if bellman_opportunities:
                print("🔍 OPORTUNIDADES COM BELLMAN-FORD:")
                for opp in bellman_opportunities[:2]:
                    path_str = " → ".join(opp['path'])
                    print(f"   ↪ {path_str}")
                    print(f"     Lucro: {opp['profit_percent']:.4f}%")
                    print()
            
            # Aguardar próxima verificação
            time.sleep(10)  # Verificar a cada 10 segundos
            
    except KeyboardInterrupt:
        print("\n\n🛑 Monitor interrompido pelo usuário")

if __name__ == "__main__":
    main()