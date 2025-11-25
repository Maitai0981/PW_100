# 🚀 Crypto Arbitrage Monitor - Real Time

Sistema completo de monitoramento de arbitragem de criptomoedas em tempo real com interface web interativa.

## 📋 Descrição

Este sistema monitora múltiplas exchanges de criptomoedas em tempo real e detecta oportunidades de arbitragem usando algoritmos otimizados (Bellman-Ford e busca triangular). O sistema é dividido em:

- **Backend**: Coleta dados reais de exchanges e detecta oportunidades
- **Frontend**: Interface web interativa com visualizações em tempo real
- **Servidor**: HTTP server para servir a interface

## ✨ Características

### Backend
- ✅ Coleta de dados em tempo real de múltiplas exchanges (CoinGecko, Binance, Kraken, Coinbase)
- ✅ Detecção de arbitragem usando algoritmos otimizados com NumPy
- ✅ Suporte para criptomoedas e moedas fiat
- ✅ Cálculo automático de taxas cruzadas
- ✅ Atualização automática a cada 30 segundos
- ✅ Exportação de dados em JSON

### Frontend
- ✅ Dashboard interativo e responsivo
- ✅ Visualização de oportunidades em tempo real
- ✅ Gráfico de histórico de oportunidades
- ✅ Visualização de rede de moedas (grafo)
- ✅ Estatísticas de mercado ao vivo
- ✅ Interface dark mode moderna

## 🛠️ Tecnologias

### Backend
- Python 3.7+
- NumPy (otimizações numéricas)
- Requests (coleta de dados)

### Frontend
- HTML5 / CSS3
- JavaScript (Vanilla)
- Chart.js (gráficos)
- Canvas API (visualização de grafo)

## 📦 Instalação

### Versão do Python

- **Mínimo:** Python 3.7+
- **Recomendado:** Python 3.8+
- **Ideal:** Python 3.10 ou 3.11

👉 **Ver detalhes:** [PYTHON_VERSIONS.md](PYTHON_VERSIONS.md)

### Opção 1: Com Ambiente Virtual (Recomendado) ⭐

**Windows:**
```bash
# 1. Configurar venv e instalar dependências
setup_venv.bat

# 2. Executar o sistema
start_venv.bat
```

**Linux / Mac:**
```bash
# 1. Dar permissão e configurar
chmod +x setup_venv.sh start_venv.sh
./setup_venv.sh

# 2. Executar o sistema
./start_venv.sh
```

### Opção 2: Instalação Global

```bash
pip install numpy requests
```

### 2. Estrutura de Arquivos

```
PW_100/
├── backend/
│   ├── __init__.py
│   ├── crypto_data_fetcher.py    # Coleta de dados das exchanges
│   └── arbitrage_engine.py       # Engine de detecção de arbitragem
├── frontend/
│   ├── index.html                # Interface HTML
│   ├── styles.css                # Estilos
│   └── app.js                    # Lógica do frontend
├── data/                         # Dados gerados (criado automaticamente)
│   ├── arbitrage_results.json
│   ├── market_data.json
│   └── history.json
├── a.py                          # Algoritmos originais
├── server.py                     # Servidor web
├── run.py                        # Launcher principal
└── README.md                     # Este arquivo
```

## 🚀 Como Usar

### Modo Completo (Backend + Frontend)

Execute o sistema completo com interface web:

```bash
python run.py
```

O sistema irá:
1. Iniciar o backend (coleta de dados e detecção)
2. Aguardar primeira coleta (10 segundos)
3. Iniciar servidor web na porta 8000
4. Abrir automaticamente o navegador

**Acesse**: http://localhost:8000/frontend/index.html

### Modo Backend Apenas

Para rodar apenas o engine de arbitragem:

```bash
python backend/arbitrage_engine.py
```

### Modo Servidor Apenas

Para rodar apenas o servidor web (se já tiver dados):

```bash
python server.py
```

## 📊 Fontes de Dados

O sistema coleta dados das seguintes fontes:

1. **CoinGecko** (API pública)
   - Preços principais de criptomoedas
   - Pares vs USD, EUR, GBP, JPY, AUD, CAD, CHF

2. **Binance** (API pública)
   - Pares de trading em tempo real
   - USDT, BTC, ETH, BNB como moedas base

3. **Kraken** (API pública)
   - Preços spot
   - Pares principais vs USD, EUR, GBP

4. **Coinbase** (API pública)
   - Preços spot
   - Pares principais vs USD, EUR

5. **Exchange Rate API**
   - Taxas de câmbio fiat

## 🎯 Algoritmos

### 1. Bellman-Ford Otimizado
- Detecta ciclos negativos no grafo de taxas
- Complexidade: O(V·E)
- Ideal para grafos densos

### 2. Busca Triangular
- Detecta arbitragem em triângulos
- Complexidade: O(V³)
- Ideal para grafos pequenos

### 3. Taxas Cruzadas
- Calcula automaticamente taxas intermediárias
- Amplia oportunidades de arbitragem

## 📈 Interface Web

### Dashboard Principal
- **Stats Cards**: Métricas principais (oportunidades, lucro, moedas, pares)
- **Lista de Oportunidades**: Top oportunidades ordenadas por lucro
- **Informações de Mercado**: Timestamp, tempo de detecção, cobertura
- **Gráfico de Histórico**: Evolução de oportunidades ao longo do tempo
- **Visualização de Rede**: Grafo interativo de moedas e rotas

### Controles
- 🔄 **Refresh**: Atualizar dados manualmente
- ⬆️⬇️ **Sort**: Ordenar oportunidades
- **Zoom**: +/- para zoom no grafo
- ⟲ **Reset**: Resetar visualização do grafo

## ⚙️ Configuração

### Intervalo de Atualização

Edite em [backend/crypto_data_fetcher.py](backend/crypto_data_fetcher.py):

```python
# Linha 185
self.data_manager = RealTimeDataManager(update_interval=30)  # segundos
```

### Frontend Auto-Refresh

Edite em [frontend/app.js](frontend/app.js):

```javascript
// Linha 12
this.updateInterval = 5000; // milissegundos
```

### Filtro de Lucro Mínimo

Edite em [backend/arbitrage_engine.py](backend/arbitrage_engine.py):

```python
# Linha 70
opportunities = [opp for opp in opportunities if opp['profit_percent'] > 0.1]
```

## 🔍 Exemplo de Saída

### Backend Console
```
🔍 ANÁLISE DE ARBITRAGEM - 14:30:45
📊 Mercado: 15 moedas, 120 pares (89.5% cobertura)
⚡ Detecção: 0.0234s

💰 3 OPORTUNIDADES ENCONTRADAS:

   #1 Lucro: 1.2340%
       Rota: BTC → ETH → USD → BTC
       Produto: 1.012340
```

### Frontend Interface
![Dashboard com cards de estatísticas, lista de oportunidades e grafo de rede]

## 🚨 Avisos Importantes

1. **Dados em Tempo Real**: Os dados são reais, mas podem ter latência
2. **Taxas de Exchange**: Não considera taxas de trading (adicione margem)
3. **Slippage**: Mercado pode mudar antes da execução
4. **Uso Educacional**: Este sistema é para fins educacionais e de pesquisa
5. **Limites de API**: Algumas APIs têm rate limits (implementa cache)

## 🐛 Troubleshooting

### "Arquivo de dados não encontrado"
- Execute primeiro o backend para gerar dados
- Verifique se a pasta `data/` foi criada

### "Erro ao buscar CoinGecko"
- Verifique sua conexão com internet
- APIs públicas podem ter rate limits

### Porta 8000 em uso
- Altere a porta em [server.py](server.py):
```python
PORT = 8080  # ou outra porta disponível
```

## 📝 Arquivos JSON

### arbitrage_results.json
```json
{
  "timestamp": "2025-01-25T14:30:45",
  "detection_time_seconds": 0.0234,
  "market": {
    "currencies": 15,
    "pairs": 120,
    "coverage_percent": 89.5
  },
  "opportunities": [
    {
      "path": ["BTC", "ETH", "USD", "BTC"],
      "profit_percent": 1.2340,
      "product": 1.012340,
      "path_length": 3
    }
  ]
}
```

## 🤝 Contribuindo

Sinta-se livre para:
- Reportar bugs
- Sugerir melhorias
- Adicionar novas exchanges
- Melhorar algoritmos

## 📄 Licença

Este projeto é de código aberto para fins educacionais.

## 👨‍💻 Autor

Sistema desenvolvido para monitoramento educacional de arbitragem em criptomoedas.

---

**⚠️ DISCLAIMER**: Este sistema é apenas para fins educacionais. Não nos responsabilizamos por perdas financeiras. Trading de criptomoedas envolve riscos.
