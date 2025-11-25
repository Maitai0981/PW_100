# 🚀 Guia de Início Rápido

## ⚡ Instalação Rápida (3 passos)

### 1️⃣ Instalar Dependências

```bash
pip install -r requirements.txt
```

Ou manualmente:

```bash
pip install numpy requests
```

### 2️⃣ Executar o Sistema

```bash
python run.py
```

### 3️⃣ Acessar Interface

O navegador abrirá automaticamente em:
```
http://localhost:8000/frontend/index.html
```

Se não abrir, acesse manualmente.

---

## 📊 O Que Você Verá

### Dashboard Principal

1. **Cards de Estatísticas** (topo)
   - 💰 Oportunidades Ativas
   - 📈 Maior Lucro (%)
   - 🪙 Moedas Monitoradas
   - 🔄 Pares Ativos

2. **Lista de Oportunidades** (esquerda)
   - Top oportunidades ordenadas por lucro
   - Rota completa da arbitragem
   - Detalhes do produto e lucro

3. **Informações de Mercado** (direita)
   - Última atualização
   - Tempo de detecção
   - Cobertura de mercado
   - Lucro médio
   - Gráfico de histórico
   - Lista de moedas ativas

4. **Visualização de Rede** (bottom)
   - Grafo interativo de moedas
   - Rotas de arbitragem destacadas
   - Controles de zoom

---

## 🎯 Primeiros Passos

### Aguardar Primeira Atualização

Ao iniciar, o sistema:
1. Conecta às exchanges (5-10 segundos)
2. Coleta dados iniciais
3. Detecta oportunidades
4. Atualiza a interface

**Primeira atualização:** ~10 segundos
**Atualizações seguintes:** A cada 30 segundos

### Interpretar Resultados

#### Oportunidade de Exemplo:

```
#1 Lucro: +1.2340%
Rota: BTC → ETH → USD → BTC
Passos: 3 | Produto: 1.012340
```

**Significa:**
- Começar com 1 BTC
- Trocar por ETH
- Trocar ETH por USD
- Trocar USD de volta por BTC
- **Resultado:** 1.012340 BTC (1.234% de lucro)

#### Cores dos Badges:

- 🟢 **Verde** (profit-high): > 1.0% de lucro
- 🟡 **Amarelo** (profit-medium): 0.5% - 1.0%
- 🔵 **Azul** (profit-low): 0.1% - 0.5%

---

## ⚙️ Configurações Rápidas

### Mudar Intervalo de Atualização

Edite `config.py`:

```python
# Atualizar a cada 60 segundos (mais lento)
DATA_UPDATE_INTERVAL = 60

# Atualizar a cada 15 segundos (mais rápido)
DATA_UPDATE_INTERVAL = 15
```

### Mudar Lucro Mínimo

```python
# Mostrar apenas oportunidades > 0.5%
MIN_PROFIT_THRESHOLD = 0.5

# Mostrar todas oportunidades > 0.01%
MIN_PROFIT_THRESHOLD = 0.01
```

### Mudar Porta do Servidor

```python
# Usar porta 3000 ao invés de 8000
WEB_SERVER_PORT = 3000
```

---

## 🔧 Modos de Execução

### Modo 1: Sistema Completo (Recomendado)

```bash
python run.py
```

**Inicia:**
- ✅ Backend (coleta e análise)
- ✅ Frontend (interface web)
- ✅ Abre navegador automaticamente

### Modo 2: Backend Apenas

```bash
python backend/arbitrage_engine.py
```

**Útil para:**
- Ver logs detalhados no console
- Rodar em servidor sem interface
- Debug e desenvolvimento

### Modo 3: Frontend Apenas

```bash
python server.py
```

**Útil para:**
- Visualizar dados já coletados
- Testar mudanças na interface
- Usar com backend rodando separadamente

---

## 📈 Monitoramento

### Console do Backend

```
🔍 ANÁLISE DE ARBITRAGEM - 14:30:45
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📊 Mercado: 15 moedas, 120 pares (89.5% cobertura)
⚡ Detecção: 0.0234s

💰 3 OPORTUNIDADES ENCONTRADAS:

   #1 Lucro: 1.2340%
       Rota: BTC → ETH → USD → BTC
       Produto: 1.012340

   #2 Lucro: 0.8750%
       Rota: USD → JPY → EUR → USD
       Produto: 1.008750
```

### Interface Web

- **Status Badge** (canto superior direito)
  - 🟢 **Online**: Conectado e atualizando
  - 🔴 **Offline**: Sem conexão ou dados

- **Gráfico de Histórico**: Mostra evolução de oportunidades

---

## ❓ Problemas Comuns

### "ModuleNotFoundError: No module named 'numpy'"

**Solução:**
```bash
pip install numpy requests
```

### "Address already in use" (Porta 8000)

**Solução 1:** Mude a porta em `config.py`:
```python
WEB_SERVER_PORT = 8080
```

**Solução 2:** Encontre e mate o processo:
```bash
# Windows
netstat -ano | findstr :8000
taskkill /PID <PID> /F

# Linux/Mac
lsof -ti:8000 | xargs kill -9
```

### Interface mostra "Aguardando dados..."

**Causa:** Backend ainda não gerou dados

**Solução:**
1. Aguarde 10-15 segundos
2. Clique no botão 🔄 Refresh
3. Verifique se backend está rodando
4. Veja logs do console

### "Erro ao buscar CoinGecko" / APIs

**Causas possíveis:**
- Sem internet
- API rate limit
- Firewall bloqueando

**Solução:**
- Verifique conexão
- Aguarde alguns minutos (rate limit)
- Use VPN se APIs estiverem bloqueadas

---

## 📱 Compatibilidade

### Navegadores Suportados

- ✅ Chrome / Edge (Recomendado)
- ✅ Firefox
- ✅ Safari
- ⚠️ IE11 (Não suportado)

### Python

- ✅ Python 3.7+
- ✅ Python 3.8+ (Recomendado)
- ✅ Python 3.9+
- ✅ Python 3.10+
- ✅ Python 3.11+

### Sistemas Operacionais

- ✅ Windows 10/11
- ✅ macOS 10.14+
- ✅ Linux (Ubuntu, Debian, etc.)

---

## 🎓 Próximos Passos

1. **Explore a Interface**
   - Clique nas oportunidades
   - Use zoom no grafo
   - Veja o histórico

2. **Customize Configurações**
   - Edite `config.py`
   - Ajuste intervalos
   - Adicione mais moedas

3. **Analise os Dados**
   - Veja arquivos em `data/`
   - Use dados para análises
   - Exporte para Excel/CSV

4. **Leia a Documentação Completa**
   - Veja `README.md`
   - Entenda os algoritmos
   - Aprenda sobre arbitragem

---

## 🆘 Ajuda

### Ver Configurações

```bash
python config.py
```

### Limpar Dados

```bash
# Windows
rmdir /s data

# Linux/Mac
rm -rf data
```

### Logs Detalhados

Edite `config.py`:
```python
VERBOSE_LOGGING = True
```

---

## 🎉 Pronto!

Seu sistema de monitoramento de arbitragem está rodando!

**Dica:** Deixe rodando por alguns minutos para acumular histórico e ver o gráfico evoluir.

---

**Problemas?** Abra uma issue ou consulte `README.md` para mais detalhes.
