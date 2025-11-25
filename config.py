"""
Arquivo de configuração centralizado para o Crypto Arbitrage Monitor
"""

# ===== CONFIGURAÇÕES DO BACKEND =====

# Intervalo de atualização dos dados (em segundos)
DATA_UPDATE_INTERVAL = 30

# Diretório onde os dados serão salvos
DATA_OUTPUT_DIR = "data"

# Lucro mínimo para considerar uma oportunidade (em %)
MIN_PROFIT_THRESHOLD = 0.1

# Número máximo de oportunidades a salvar no arquivo
MAX_OPPORTUNITIES_TO_SAVE = 20

# Número de entradas de histórico a manter
HISTORY_SIZE = 100

# ===== CONFIGURAÇÕES DAS EXCHANGES =====

# CoinGecko: IDs das criptomoedas a monitorar
COINGECKO_COINS = [
    'bitcoin', 'ethereum', 'cardano', 'polkadot', 'binancecoin',
    'ripple', 'solana', 'dogecoin', 'litecoin', 'chainlink'
]

# CoinGecko: Moedas fiat a usar como referência
COINGECKO_VS_CURRENCIES = ['usd', 'eur', 'gbp', 'jpy', 'aud', 'cad', 'chf']

# Binance: Pares principais a monitorar
BINANCE_PAIRS = [
    'BTCUSDT', 'ETHUSDT', 'BNBUSDT', 'ADAUSDT', 'DOTUSDT',
    'XRPUSDT', 'SOLUSDT', 'DOGEUSDT', 'LTCUSDT', 'LINKUSDT',
    'ETHBTC', 'BNBBTC', 'ADABTC', 'DOTBTC', 'XRPBTC',
    'ETHBNB', 'ADAETH', 'DOTETH'
]

# Kraken: Pares a monitorar
KRAKEN_PAIRS = [
    'XXBTZUSD', 'XETHZUSD', 'ADAUSD', 'DOTUSD',
    'XXBTZEUR', 'XETHZEUR', 'XXBTZGBP', 'XETHZGBP'
]

# Coinbase: Pares a monitorar
COINBASE_PAIRS = [
    'BTC-USD', 'ETH-USD', 'ADA-USD', 'DOT-USD',
    'BTC-EUR', 'ETH-EUR'
]

# Moedas fiat para taxas de câmbio
FIAT_CURRENCIES = ['EUR', 'GBP', 'JPY', 'AUD', 'CAD', 'CHF']

# ===== CONFIGURAÇÕES DE TIMEOUT =====

# Timeout para requisições HTTP (em segundos)
HTTP_TIMEOUT = 10

# Timeout reduzido para Coinbase (endpoint individual)
COINBASE_TIMEOUT = 5

# ===== CONFIGURAÇÕES DO FRONTEND =====

# Porta do servidor web
WEB_SERVER_PORT = 8000

# Intervalo de auto-refresh do frontend (em milissegundos)
FRONTEND_UPDATE_INTERVAL = 5000

# ===== CONFIGURAÇÕES DE ALGORITMOS =====

# Usar Bellman-Ford otimizado por padrão
USE_OPTIMIZED_BELLMAN_FORD = True

# Usar busca triangular para grafos pequenos (número máximo de moedas)
MAX_CURRENCIES_FOR_TRIANGLE_SEARCH = 15

# Frequência de busca triangular (a cada N ciclos)
TRIANGLE_SEARCH_FREQUENCY = 10

# ===== CONFIGURAÇÕES DE LOGGING =====

# Mostrar logs detalhados
VERBOSE_LOGGING = True

# Mostrar estatísticas de performance a cada N verificações
STATS_FREQUENCY = 5

# ===== CONFIGURAÇÕES DE CACHE =====

# Tempo de cache para dados (em segundos)
CACHE_TIMEOUT = 10

# ===== MAPEAMENTO DE SÍMBOLOS =====

# Mapear IDs do CoinGecko para símbolos comuns
COINGECKO_SYMBOL_MAP = {
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

# Mapear nomes estranhos da Kraken
KRAKEN_NAME_MAP = {
    'XXBTZUSD': 'BTC/USD',
    'XETHZUSD': 'ETH/USD',
    'ADAUSD': 'ADA/USD',
    'DOTUSD': 'DOT/USD',
    'XXBTZEUR': 'BTC/EUR',
    'XETHZEUR': 'ETH/EUR',
    'XXBTZGBP': 'BTC/GBP',
    'XETHZGBP': 'ETH/GBP'
}

# ===== URLs DAS APIS =====

COINGECKO_API_URL = "https://api.coingecko.com/api/v3/simple/price"
BINANCE_API_URL = "https://api.binance.com/api/v3/ticker/price"
KRAKEN_API_URL = "https://api.kraken.com/0/public/Ticker"
COINBASE_API_URL = "https://api.coinbase.com/v2/prices"
EXCHANGERATE_API_URL = "https://api.exchangerate-api.com/v4/latest/USD"

# ===== CONFIGURAÇÕES AVANÇADAS =====

# Calcular taxas cruzadas automaticamente
CALCULATE_CROSS_RATES = True

# Incluir taxas inversas automaticamente
INCLUDE_INVERSE_RATES = True

# Variação de mercado simulada para testes (min, max)
# Desabilite (None) para usar apenas dados reais
MARKET_VARIATION = None  # (0.998, 1.002) para ±0.2%


def get_config():
    """Retorna todas as configurações como dicionário"""
    return {
        key: value
        for key, value in globals().items()
        if key.isupper() and not key.startswith('_')
    }


def print_config():
    """Imprime configurações atuais"""
    print("=" * 60)
    print("CONFIGURAÇÕES ATUAIS")
    print("=" * 60)

    config = get_config()
    for key, value in sorted(config.items()):
        print(f"{key:.<40} {value}")

    print("=" * 60)


if __name__ == "__main__":
    print_config()
