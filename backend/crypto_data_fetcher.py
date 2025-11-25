import requests
import time
import json
from typing import List, Tuple, Dict, Optional
from datetime import datetime
import threading
from collections import defaultdict

class CryptoDataFetcher:
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
        self.cache = {}
        self.cache_timeout = 10  # segundos

    def fetch_coingecko_prices(self) -> Dict[str, float]:
        """Busca preços do CoinGecko (sem API key necessária) - Endpoint otimizado"""
        try:
            # Endpoint mais simples e direto para preços
            url = "https://api.coingecko.com/api/v3/simple/price"
            params = {
                'ids': 'bitcoin,ethereum,binancecoin,ripple,solana,cardano,polkadot,chainlink,litecoin,stellar',
                'vs_currencies': 'usd,brl,eur'
            }

            response = self.session.get(url, params=params, timeout=10)
            
            # Verificar rate limit
            if response.status_code == 429:
                print("⚠️  Rate limit do CoinGecko atingido, aguardando...")
                time.sleep(30)
                return {}
                
            response.raise_for_status()
            data = response.json()

            # Mapear para símbolos comuns
            symbol_map = {
                'bitcoin': 'BTC',
                'ethereum': 'ETH',
                'binancecoin': 'BNB',
                'ripple': 'XRP', 
                'solana': 'SOL',
                'cardano': 'ADA',
                'polkadot': 'DOT',
                'chainlink': 'LINK',
                'litecoin': 'LTC',
                'stellar': 'XLM'
            }

            prices = {}
            for coin_id, coin_data in data.items():
                symbol = symbol_map.get(coin_id, coin_id.upper())
                for currency, price in coin_data.items():
                    prices[f"{symbol}/{currency.upper()}"] = float(price)

            return prices

        except Exception as e:
            print(f"⚠️  Erro ao buscar CoinGecko: {e}")
            return {}

    def fetch_binance_prices(self) -> Dict[str, float]:
        """Busca preços da Binance (API pública) - Método mais robusto"""
        try:
            # Focar nos pares mais importantes para reduzir carga
            relevant_symbols = [
                'BTCUSDT', 'ETHUSDT', 'BNBUSDT', 'ADAUSDT', 'DOTUSDT',
                'XRPUSDT', 'SOLUSDT', 'LTCUSDT', 'LINKUSDT', 'XLMUSDT',
                'BTCBRL', 'ETHBRL', 'BNBBRL', 'ADABRL'
            ]
            
            prices = {}
            for symbol in relevant_symbols:
                try:
                    url = f"https://api.binance.com/api/v3/ticker/price?symbol={symbol}"
                    response = self.session.get(url, timeout=5)
                    
                    if response.status_code == 200:
                        data = response.json()
                        
                        # Converter símbolo para formato padrão
                        if symbol.endswith('USDT'):
                            base = symbol[:-4]
                            prices[f"{base}/USDT"] = float(data['price'])
                        elif symbol.endswith('BRL'):
                            base = symbol[:-3] 
                            prices[f"{base}/BRL"] = float(data['price'])
                            
                except Exception as e:
                    continue  # Continua com próximos símbolos se um falhar

            return prices

        except Exception as e:
            print(f"⚠️  Erro ao buscar Binance: {e}")
            return {}

    def fetch_coinbase_prices(self) -> Dict[str, float]:
        """Busca preços da Coinbase (API pública) - Método mais eficiente"""
        try:
            # Coinbase tem endpoint batch para múltiplos pares
            pairs = ['BTC-USD', 'ETH-USD', 'BTC-BRL', 'ETH-BRL', 'BTC-EUR', 'ETH-EUR']
            prices = {}

            for pair in pairs:
                try:
                    url = f"https://api.coinbase.com/v2/prices/{pair}/spot"
                    response = self.session.get(url, timeout=5)
                    
                    if response.status_code == 200:
                        data = response.json()
                        if 'data' in data and 'amount' in data['data']:
                            formatted_pair = pair.replace('-', '/')
                            prices[formatted_pair] = float(data['data']['amount'])
                    
                    # Pequena pausa para evitar rate limit
                    time.sleep(0.1)
                    
                except Exception as e:
                    continue

            return prices

        except Exception as e:
            print(f"⚠️  Erro ao buscar Coinbase: {e}")
            return {}

    def fetch_awesomeapi_rates(self) -> Dict[str, float]:
        """Busca taxas de câmbio fiat da AwesomeAPI (especializada em BRL)"""
        try:
            url = "https://economia.awesomeapi.com.br/json/last/USD-BRL,EUR-BRL,BTC-BRL"
            response = self.session.get(url, timeout=10)
            response.raise_for_status()
            data = response.json()

            prices = {}
            
            # Mapear resposta da AwesomeAPI
            if 'USDBRL' in data:
                prices['USD/BRL'] = float(data['USDBRL']['bid'])
                prices['BRL/USD'] = 1.0 / float(data['USDBRL']['bid'])
                
            if 'EURBRL' in data:
                prices['EUR/BRL'] = float(data['EURBRL']['bid']) 
                prices['BRL/EUR'] = 1.0 / float(data['EURBRL']['bid'])
                
            if 'BTCBRL' in data:
                prices['BTC/BRL'] = float(data['BTCBRL']['bid'])
                prices['BRL/BTC'] = 1.0 / float(data['BTCBRL']['bid'])

            return prices

        except Exception as e:
            print(f"⚠️  Erro ao buscar AwesomeAPI: {e}")
            return {}

    def fetch_all_rates(self) -> List[Tuple[str, str, float]]:
        """Busca todas as taxas de todas as exchanges com gestão de erro melhorada"""
        all_prices = {}

        # Fontes prioritárias - APIs mais confiáveis
        sources = [
            ('CoinGecko', self.fetch_coingecko_prices),
            ('Binance', self.fetch_binance_prices),
            ('AwesomeAPI', self.fetch_awesomeapi_rates),
            ('Coinbase', self.fetch_coinbase_prices)
        ]

        for source_name, fetch_func in sources:
            try:
                print(f"🔍 Coletando dados de {source_name}...")
                prices = fetch_func()
                if prices:
                    all_prices.update(prices)
                    print(f"✅ {source_name}: {len(prices)} pares obtidos")
                else:
                    print(f"⚠️  {source_name}: Nenhum dado obtido")
                    
                # Pausa estratégica entre requests
                time.sleep(1)
                
            except Exception as e:
                print(f"❌ {source_name}: {e}")
                continue

        # Converter para formato de taxa (from, to, rate)
        rates = []
        processed_pairs = set()

        for pair, price in all_prices.items():
            if '/' in pair:
                from_curr, to_curr = pair.split('/')

                # Adicionar taxa direta
                if (from_curr, to_curr) not in processed_pairs and price > 0:
                    rates.append((from_curr, to_curr, price))
                    processed_pairs.add((from_curr, to_curr))

                # Adicionar taxa inversa se possível
                if price > 0 and (to_curr, from_curr) not in processed_pairs:
                    inverse_price = 1.0 / price
                    rates.append((to_curr, from_curr, inverse_price))
                    processed_pairs.add((to_curr, from_curr))

        print(f"📊 Total de {len(rates)} taxas coletadas de {len(processed_pairs)} pares únicos")
        return rates

    def get_market_summary(self, rates: List[Tuple[str, str, float]]) -> Dict:
        """Gera resumo do mercado"""
        currencies = set()
        crypto_currencies = set()
        fiat_currencies = set()
        
        fiat_list = ['USD', 'BRL', 'EUR', 'GBP', 'JPY', 'CAD']
        
        for from_curr, to_curr, _ in rates:
            currencies.add(from_curr)
            currencies.add(to_curr)
            
            if from_curr in fiat_list:
                fiat_currencies.add(from_curr)
            else:
                crypto_currencies.add(from_curr)
                
            if to_curr in fiat_list:
                fiat_currencies.add(to_curr)
            else:
                crypto_currencies.add(to_curr)

        return {
            'timestamp': datetime.now().isoformat(),
            'total_currencies': len(currencies),
            'total_crypto': len(crypto_currencies),
            'total_fiat': len(fiat_currencies),
            'total_pairs': len(rates),
            'crypto_currencies': sorted(list(crypto_currencies)),
            'fiat_currencies': sorted(list(fiat_currencies))
        }


class RealTimeDataManager:
    """Gerenciador de dados em tempo real com cache e atualização periódica"""

    def __init__(self, update_interval: int = 60):  # Aumentado para 60s para evitar rate limit
        self.fetcher = CryptoDataFetcher()
        self.update_interval = update_interval
        self.current_rates = []
        self.market_summary = {}
        self.last_update = None
        self.is_running = False
        self.update_thread = None
        self.callbacks = []

    def add_callback(self, callback):
        """Adiciona callback para quando dados forem atualizados"""
        self.callbacks.append(callback)

    def start(self):
        """Inicia atualização contínua em background"""
        if not self.is_running:
            self.is_running = True
            self.update_thread = threading.Thread(target=self._update_loop, daemon=True)
            self.update_thread.start()
            print(f"🚀 Manager de dados iniciado (atualização a cada {self.update_interval}s)")

    def stop(self):
        """Para atualização"""
        self.is_running = False
        if self.update_thread:
            self.update_thread.join(timeout=5)
        print("🛑 Manager de dados parado")

    def _update_loop(self):
        """Loop de atualização contínua"""
        while self.is_running:
            try:
                self.update_data()
                # Intervalo adaptativo baseado no sucesso da coleta
                time.sleep(self.update_interval)
            except Exception as e:
                print(f"❌ Erro no loop de atualização: {e}")
                # Espera mais longe em caso de erro
                time.sleep(30)

    def update_data(self):
        """Atualiza dados uma vez"""
        print(f"\n🔄 Atualizando dados... {datetime.now().strftime('%H:%M:%S')}")

        try:
            # Buscar taxas
            self.current_rates = self.fetcher.fetch_all_rates()
            self.market_summary = self.fetcher.get_market_summary(self.current_rates)
            self.last_update = datetime.now()

            print(f"✅ Atualização completa: {len(self.current_rates)} taxas, "
                  f"{self.market_summary['total_currencies']} moedas "
                  f"({self.market_summary['total_crypto']} cripto, "
                  f"{self.market_summary['total_fiat']} fiat)")

            # Notificar callbacks
            for callback in self.callbacks:
                try:
                    callback(self.current_rates, self.market_summary)
                except Exception as e:
                    print(f"⚠️  Erro em callback: {e}")

        except Exception as e:
            print(f"❌ Erro ao atualizar dados: {e}")

    def get_current_data(self) -> Tuple[List[Tuple[str, str, float]], Dict]:
        """Retorna dados atuais"""
        return self.current_rates, self.market_summary

    def save_to_file(self, filepath: str = "market_data.json"):
        """Salva dados atuais em arquivo JSON"""
        import os
        os.makedirs(os.path.dirname(filepath), exist_ok=True)

        data = {
            'timestamp': self.last_update.isoformat() if self.last_update else None,
            'summary': self.market_summary,
            'rates': [
                {'from': from_curr, 'to': to_curr, 'rate': rate}
                for from_curr, to_curr, rate in self.current_rates
            ]
        }

        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

        print(f"💾 Dados salvos em: {filepath}")
        return filepath


# Função de exemplo para demonstrar uso
def print_market_summary(rates, summary):
    """Callback de exemplo para mostrar resumo do mercado"""
    print(f"📈 Resumo: {summary['total_crypto']} criptomoedas, "
          f"{summary['total_fiat']} moedas fiat, "
          f"{summary['total_pairs']} pares de trading")


if __name__ == "__main__":
    # Teste do fetcher
    print("🧪 Testando coleta de dados em tempo real...\n")
    print("📋 Fontes configuradas: CoinGecko, Binance, Coinbase, AwesomeAPI")

    manager = RealTimeDataManager(update_interval=60)
    manager.add_callback(print_market_summary)

    # Atualização única para teste
    print("\n🔍 Executando primeira coleta...")
    manager.update_data()

    rates, summary = manager.get_current_data()

    print(f"\n📊 PRINCIPAIS TAXAS:")
    # Mostrar algumas taxas relevantes
    relevant_pairs = [rate for rate in rates if any(currency in ['BRL', 'USD'] for currency in [rate[0], rate[1]])]
    
    for from_curr, to_curr, rate in relevant_pairs[:15]:
        if rate < 1000:  # Filtrar taxas muito altas para melhor visualização
            print(f"   {from_curr} → {to_curr}: {rate:.6f}")

    # Salvar em arquivo
    filepath = manager.save_to_file("dados_mercado.json")
    
    print(f"\n🎯 Dica: Configure o intervalo de atualização para no mínimo 60 segundos")
    print("   para evitar rate limiting das APIs públicas gratuitas.")  