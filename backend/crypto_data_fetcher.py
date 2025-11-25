"""
Backend: Coleta de dados em tempo real de exchanges de criptomoedas
Busca taxas reais de múltiplas fontes sem necessidade de API key
"""

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
        """Busca preços do CoinGecko (sem API key necessária)"""
        try:
            url = "https://api.coingecko.com/api/v3/simple/price"
            params = {
                'ids': 'bitcoin,ethereum,cardano,polkadot,binancecoin,ripple,solana,dogecoin,litecoin,chainlink',
                'vs_currencies': 'usd,eur,gbp,jpy,aud,cad,chf'
            }

            response = self.session.get(url, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()

            # Mapear para símbolos comuns
            symbol_map = {
                'bitcoin': 'BTC',
                'ethereum': 'ETH',
                'cardano': 'ADA',
                'polkadot': 'DOT',
                'binancecoin': 'BNB',
                'ripple': 'XRP',
                'solana': 'SOL',
                'dogecoin': 'DOGE',
                'litecoin': 'LTC',
                'chainlink': 'LINK'
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
        """Busca preços da Binance (API pública)"""
        try:
            url = "https://api.binance.com/api/v3/ticker/price"
            response = self.session.get(url, timeout=10)
            response.raise_for_status()
            data = response.json()

            prices = {}
            # Focar em pares principais
            relevant_pairs = [
                'BTCUSDT', 'ETHUSDT', 'BNBUSDT', 'ADAUSDT', 'DOTUSDT',
                'XRPUSDT', 'SOLUSDT', 'DOGEUSDT', 'LTCUSDT', 'LINKUSDT',
                'ETHBTC', 'BNBBTC', 'ADABTC', 'DOTBTC', 'XRPBTC',
                'ETHBNB', 'ADAETH', 'DOTETH'
            ]

            for item in data:
                symbol = item['symbol']
                if symbol in relevant_pairs:
                    # Converter BTCUSDT -> BTC/USDT
                    if symbol.endswith('USDT'):
                        base = symbol[:-4]
                        prices[f"{base}/USDT"] = float(item['price'])
                    elif symbol.endswith('BTC'):
                        base = symbol[:-3]
                        prices[f"{base}/BTC"] = float(item['price'])
                    elif symbol.endswith('ETH'):
                        base = symbol[:-3]
                        prices[f"{base}/ETH"] = float(item['price'])
                    elif symbol.endswith('BNB'):
                        base = symbol[:-3]
                        prices[f"{base}/BNB"] = float(item['price'])

            return prices

        except Exception as e:
            print(f"⚠️  Erro ao buscar Binance: {e}")
            return {}

    def fetch_kraken_prices(self) -> Dict[str, float]:
        """Busca preços da Kraken (API pública)"""
        try:
            url = "https://api.kraken.com/0/public/Ticker"
            pairs = [
                'XXBTZUSD', 'XETHZUSD', 'ADAUSD', 'DOTUSD',
                'XXBTZEUR', 'XETHZEUR', 'XXBTZGBP', 'XETHZGBP'
            ]
            params = {'pair': ','.join(pairs)}

            response = self.session.get(url, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()

            if data.get('error'):
                return {}

            prices = {}
            # Mapear nomes estranhos da Kraken
            name_map = {
                'XXBTZUSD': 'BTC/USD',
                'XETHZUSD': 'ETH/USD',
                'ADAUSD': 'ADA/USD',
                'DOTUSD': 'DOT/USD',
                'XXBTZEUR': 'BTC/EUR',
                'XETHZEUR': 'ETH/EUR',
                'XXBTZGBP': 'BTC/GBP',
                'XETHZGBP': 'ETH/GBP'
            }

            for pair_key, pair_data in data.get('result', {}).items():
                if pair_key in name_map:
                    prices[name_map[pair_key]] = float(pair_data['c'][0])

            return prices

        except Exception as e:
            print(f"⚠️  Erro ao buscar Kraken: {e}")
            return {}

    def fetch_coinbase_prices(self) -> Dict[str, float]:
        """Busca preços da Coinbase (API pública)"""
        try:
            # Coinbase usa endpoints individuais
            pairs = ['BTC-USD', 'ETH-USD', 'ADA-USD', 'DOT-USD', 'BTC-EUR', 'ETH-EUR']
            prices = {}

            for pair in pairs:
                try:
                    url = f"https://api.coinbase.com/v2/prices/{pair}/spot"
                    response = self.session.get(url, timeout=5)
                    response.raise_for_status()
                    data = response.json()

                    if 'data' in data and 'amount' in data['data']:
                        formatted_pair = pair.replace('-', '/')
                        prices[formatted_pair] = float(data['data']['amount'])
                except:
                    continue

            return prices

        except Exception as e:
            print(f"⚠️  Erro ao buscar Coinbase: {e}")
            return {}

    def fetch_all_rates(self) -> List[Tuple[str, str, float]]:
        """Busca todas as taxas de todas as exchanges"""
        all_prices = {}

        # Buscar de múltiplas fontes em paralelo
        sources = [
            ('CoinGecko', self.fetch_coingecko_prices),
            ('Binance', self.fetch_binance_prices),
            ('Kraken', self.fetch_kraken_prices),
            ('Coinbase', self.fetch_coinbase_prices)
        ]

        for source_name, fetch_func in sources:
            try:
                prices = fetch_func()
                if prices:
                    all_prices.update(prices)
                    print(f"✅ {source_name}: {len(prices)} pares obtidos")
            except Exception as e:
                print(f"❌ {source_name}: {e}")

        # Converter para formato de taxa (from, to, rate)
        rates = []
        processed_pairs = set()

        for pair, price in all_prices.items():
            if '/' in pair:
                from_curr, to_curr = pair.split('/')

                # Adicionar taxa direta
                if (from_curr, to_curr) not in processed_pairs:
                    rates.append((from_curr, to_curr, price))
                    processed_pairs.add((from_curr, to_curr))

                # Adicionar taxa inversa
                if price > 0 and (to_curr, from_curr) not in processed_pairs:
                    rates.append((to_curr, from_curr, 1.0 / price))
                    processed_pairs.add((to_curr, from_curr))

        # Adicionar taxas de moedas fiat
        fiat_rates = self._get_fiat_rates()
        rates.extend(fiat_rates)

        # Calcular taxas cruzadas para ampliar oportunidades
        cross_rates = self._calculate_cross_rates(rates)
        rates.extend(cross_rates)

        return rates

    def _get_fiat_rates(self) -> List[Tuple[str, str, float]]:
        """Busca taxas de câmbio fiat"""
        try:
            url = "https://api.exchangerate-api.com/v4/latest/USD"
            response = self.session.get(url, timeout=10)
            response.raise_for_status()
            data = response.json()

            rates = []
            currencies = ['EUR', 'GBP', 'JPY', 'AUD', 'CAD', 'CHF']

            for currency in currencies:
                if currency in data['rates']:
                    rate = data['rates'][currency]
                    rates.append(('USD', currency, rate))
                    rates.append((currency, 'USD', 1.0 / rate))

            # Adicionar cruzamentos fiat
            for i, curr1 in enumerate(currencies):
                for curr2 in currencies[i+1:]:
                    if curr1 in data['rates'] and curr2 in data['rates']:
                        rate = data['rates'][curr2] / data['rates'][curr1]
                        rates.append((curr1, curr2, rate))
                        rates.append((curr2, curr1, 1.0 / rate))

            print(f"✅ Fiat: {len(rates)} taxas obtidas")
            return rates

        except Exception as e:
            print(f"⚠️  Erro ao buscar taxas fiat: {e}")
            return []

    def _calculate_cross_rates(self, existing_rates: List[Tuple[str, str, float]]) -> List[Tuple[str, str, float]]:
        """Calcula taxas cruzadas a partir das existentes"""
        # Criar dicionário de taxas
        rate_dict = defaultdict(dict)
        for from_curr, to_curr, rate in existing_rates:
            rate_dict[from_curr][to_curr] = rate

        cross_rates = []
        currencies = list(rate_dict.keys())

        # Calcular algumas taxas cruzadas importantes
        for curr_a in currencies:
            for curr_b in currencies:
                if curr_a != curr_b and curr_b not in rate_dict[curr_a]:
                    # Tentar encontrar moeda intermediária
                    for curr_mid in currencies:
                        if (curr_mid in rate_dict[curr_a] and
                            curr_b in rate_dict[curr_mid]):
                            rate = rate_dict[curr_a][curr_mid] * rate_dict[curr_mid][curr_b]
                            cross_rates.append((curr_a, curr_b, rate))
                            break

        if cross_rates:
            print(f"✅ Cross-rates: {len(cross_rates)} taxas calculadas")

        return cross_rates

    def get_market_summary(self, rates: List[Tuple[str, str, float]]) -> Dict:
        """Gera resumo do mercado"""
        currencies = set()
        for from_curr, to_curr, _ in rates:
            currencies.add(from_curr)
            currencies.add(to_curr)

        return {
            'timestamp': datetime.now().isoformat(),
            'total_currencies': len(currencies),
            'total_pairs': len(rates),
            'currencies': sorted(list(currencies))
        }


class RealTimeDataManager:
    """Gerenciador de dados em tempo real com cache e atualização periódica"""

    def __init__(self, update_interval: int = 30):
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
            print("🚀 Manager de dados iniciado")

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
                time.sleep(self.update_interval)
            except Exception as e:
                print(f"❌ Erro no loop de atualização: {e}")
                time.sleep(5)

    def update_data(self):
        """Atualiza dados uma vez"""
        print(f"\n🔄 Atualizando dados... {datetime.now().strftime('%H:%M:%S')}")

        try:
            # Buscar taxas
            self.current_rates = self.fetcher.fetch_all_rates()
            self.market_summary = self.fetcher.get_market_summary(self.current_rates)
            self.last_update = datetime.now()

            print(f"✅ Atualização completa: {len(self.current_rates)} taxas, "
                  f"{self.market_summary['total_currencies']} moedas")

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

    def save_to_file(self, filepath: str = "data/market_data.json"):
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

        with open(filepath, 'w') as f:
            json.dump(data, f, indent=2)

        return filepath


if __name__ == "__main__":
    # Teste do fetcher
    print("🧪 Testando coleta de dados em tempo real...\n")

    manager = RealTimeDataManager(update_interval=60)

    # Atualização única para teste
    manager.update_data()

    rates, summary = manager.get_current_data()

    print(f"\n📊 RESUMO:")
    print(f"   Moedas: {summary['total_currencies']}")
    print(f"   Pares: {summary['total_pairs']}")
    print(f"   Lista de moedas: {', '.join(summary['currencies'][:10])}...")

    # Mostrar algumas taxas
    print(f"\n💱 ALGUMAS TAXAS:")
    for from_curr, to_curr, rate in rates[:10]:
        print(f"   {from_curr} → {to_curr}: {rate:.8f}")

    # Salvar em arquivo
    filepath = manager.save_to_file()
    print(f"\n💾 Dados salvos em: {filepath}")
