/**
 * Frontend: Aplicação JavaScript para visualização de arbitragem
 * Lê dados do arquivo JSON gerado pelo backend
 */

class ArbitrageApp {
    constructor() {
        this.dataPath = '../data/arbitrage_results.json';
        this.historyPath = '../data/history.json';
        this.updateInterval = 5000; // 5 segundos
        this.currentData = null;
        this.historyData = [];
        this.chart = null;
        this.networkCanvas = null;
        this.networkCtx = null;
        this.zoom = 1;
        this.pan = { x: 0, y: 0 };

        this.init();
    }

    async init() {
        console.log('🚀 Inicializando Arbitrage App...');

        // Inicializar elementos
        this.initElements();
        this.initEventListeners();
        this.initNetwork();

        // Carregar dados iniciais
        await this.loadData();

        // Iniciar atualização automática
        this.startAutoUpdate();

        console.log('✅ App inicializado');
    }

    initElements() {
        // Status
        this.statusBadge = document.getElementById('statusBadge');
        this.statusText = document.getElementById('statusText');

        // Stats
        this.totalOpportunitiesEl = document.getElementById('totalOpportunities');
        this.maxProfitEl = document.getElementById('maxProfit');
        this.totalCurrenciesEl = document.getElementById('totalCurrencies');
        this.totalPairsEl = document.getElementById('totalPairs');

        // Opportunities
        this.opportunitiesListEl = document.getElementById('opportunitiesList');

        // Market Info
        this.lastUpdateEl = document.getElementById('lastUpdate');
        this.detectionTimeEl = document.getElementById('detectionTime');
        this.marketCoverageEl = document.getElementById('marketCoverage');
        this.avgProfitEl = document.getElementById('avgProfit');
        this.currenciesTagsEl = document.getElementById('currenciesTags');

        // Chart
        this.initChart();
    }

    initChart() {
        const canvas = document.getElementById('historyChart');
        const ctx = canvas.getContext('2d');

        this.chart = new Chart(ctx, {
            type: 'line',
            data: {
                labels: [],
                datasets: [{
                    label: 'Oportunidades',
                    data: [],
                    borderColor: '#6366f1',
                    backgroundColor: 'rgba(99, 102, 241, 0.1)',
                    borderWidth: 2,
                    tension: 0.4,
                    fill: true
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        display: false
                    }
                },
                scales: {
                    y: {
                        beginAtZero: true,
                        grid: {
                            color: 'rgba(99, 102, 241, 0.1)'
                        },
                        ticks: {
                            color: '#94a3b8'
                        }
                    },
                    x: {
                        grid: {
                            display: false
                        },
                        ticks: {
                            color: '#94a3b8'
                        }
                    }
                }
            }
        });
    }

    initNetwork() {
        this.networkCanvas = document.getElementById('networkCanvas');
        this.networkCtx = this.networkCanvas.getContext('2d');

        // Ajustar tamanho do canvas
        this.resizeCanvas();
        window.addEventListener('resize', () => this.resizeCanvas());
    }

    resizeCanvas() {
        const container = this.networkCanvas.parentElement;
        this.networkCanvas.width = container.clientWidth;
        this.networkCanvas.height = container.clientHeight;
    }

    initEventListeners() {
        // Refresh button
        document.getElementById('refreshBtn').addEventListener('click', () => {
            this.loadData();
        });

        // Sort button
        document.getElementById('sortBtn').addEventListener('click', () => {
            this.sortOpportunities();
        });

        // Zoom buttons
        document.getElementById('zoomInBtn').addEventListener('click', () => {
            this.zoom *= 1.2;
            this.drawNetwork();
        });

        document.getElementById('zoomOutBtn').addEventListener('click', () => {
            this.zoom *= 0.8;
            this.drawNetwork();
        });

        document.getElementById('resetZoomBtn').addEventListener('click', () => {
            this.zoom = 1;
            this.pan = { x: 0, y: 0 };
            this.drawNetwork();
        });
    }

    async loadData() {
        try {
            // Carregar dados principais
            const response = await fetch(this.dataPath + '?t=' + Date.now());
            if (!response.ok) {
                throw new Error('Arquivo de dados não encontrado');
            }

            this.currentData = await response.json();

            // Carregar histórico
            try {
                const historyResponse = await fetch(this.historyPath + '?t=' + Date.now());
                if (historyResponse.ok) {
                    this.historyData = await historyResponse.json();
                }
            } catch (e) {
                console.warn('Histórico não disponível');
            }

            // Atualizar UI
            this.updateUI();
            this.updateStatus('online');

        } catch (error) {
            console.error('Erro ao carregar dados:', error);
            this.updateStatus('offline');
        }
    }

    updateUI() {
        if (!this.currentData) return;

        // Atualizar stats
        this.updateStats();

        // Atualizar oportunidades
        this.updateOpportunities();

        // Atualizar info de mercado
        this.updateMarketInfo();

        // Atualizar gráfico
        this.updateChart();

        // Atualizar rede
        this.drawNetwork();
    }

    updateStats() {
        const { market, statistics } = this.currentData;

        this.totalOpportunitiesEl.textContent = statistics.total_found;
        this.maxProfitEl.textContent = statistics.max_profit.toFixed(4) + '%';
        this.totalCurrenciesEl.textContent = market.currencies;
        this.totalPairsEl.textContent = market.pairs;
    }

    updateOpportunities() {
        const { opportunities } = this.currentData;

        if (opportunities.length === 0) {
            this.opportunitiesListEl.innerHTML = `
                <div class="empty-state">
                    <div class="empty-icon">📭</div>
                    <p>Nenhuma oportunidade encontrada</p>
                    <small>Mercado eficiente no momento</small>
                </div>
            `;
            return;
        }

        this.opportunitiesListEl.innerHTML = opportunities
            .map((opp, index) => this.createOpportunityCard(opp, index + 1))
            .join('');
    }

    createOpportunityCard(opp, rank) {
        const profitClass = opp.profit_percent > 1 ? 'profit-high' :
                           opp.profit_percent > 0.5 ? 'profit-medium' : 'profit-low';

        const pathHtml = opp.path.map((curr, idx) => {
            if (idx === opp.path.length - 1) {
                return `<span class="currency-badge">${curr}</span>`;
            }
            return `
                <span class="currency-badge">${curr}</span>
                <span class="arrow">→</span>
            `;
        }).join('');

        return `
            <div class="opportunity-card">
                <div class="opportunity-header">
                    <span class="opportunity-rank">#${rank}</span>
                    <span class="profit-badge ${profitClass}">
                        +${opp.profit_percent.toFixed(4)}%
                    </span>
                </div>
                <div class="opportunity-path">
                    ${pathHtml}
                </div>
                <div class="opportunity-details">
                    <span>Passos: ${opp.path_length}</span>
                    <span>Produto: ${opp.product.toFixed(6)}</span>
                </div>
            </div>
        `;
    }

    updateMarketInfo() {
        const { timestamp, detection_time_seconds, market, statistics } = this.currentData;

        // Formatar timestamp
        const date = new Date(timestamp);
        this.lastUpdateEl.textContent = date.toLocaleTimeString('pt-BR');

        // Tempo de detecção
        this.detectionTimeEl.textContent = (detection_time_seconds * 1000).toFixed(2) + ' ms';

        // Cobertura
        this.marketCoverageEl.textContent = market.coverage_percent.toFixed(1) + '%';

        // Lucro médio
        this.avgProfitEl.textContent = statistics.avg_profit.toFixed(4) + '%';

        // Moedas
        if (market.all_currencies) {
            this.currenciesTagsEl.innerHTML = market.all_currencies
                .map(curr => `<span class="currency-tag">${curr}</span>`)
                .join('');
        }
    }

    updateChart() {
        if (!this.chart || this.historyData.length === 0) return;

        // Últimos 20 pontos
        const recent = this.historyData.slice(-20);

        const labels = recent.map(h => {
            const date = new Date(h.timestamp);
            return date.toLocaleTimeString('pt-BR', { hour: '2-digit', minute: '2-digit' });
        });

        const data = recent.map(h => h.count);

        this.chart.data.labels = labels;
        this.chart.data.datasets[0].data = data;
        this.chart.update('none'); // Update without animation
    }

    drawNetwork() {
        if (!this.networkCtx || !this.currentData) return;

        const { opportunities, market } = this.currentData;
        const canvas = this.networkCanvas;
        const ctx = this.networkCtx;

        // Limpar canvas
        ctx.clearRect(0, 0, canvas.width, canvas.height);

        // Se não houver dados, mostrar mensagem
        if (!market.all_currencies || market.all_currencies.length === 0) {
            ctx.fillStyle = '#64748b';
            ctx.font = '16px Inter';
            ctx.textAlign = 'center';
            ctx.fillText('Aguardando dados...', canvas.width / 2, canvas.height / 2);
            return;
        }

        // Criar nós para cada moeda
        const currencies = market.all_currencies;
        const nodes = this.createNodes(currencies, canvas);

        // Desenhar conexões (oportunidades de arbitragem)
        if (opportunities.length > 0) {
            this.drawOpportunityPaths(ctx, nodes, opportunities.slice(0, 3)); // Top 3
        }

        // Desenhar nós
        this.drawNodes(ctx, nodes, currencies);
    }

    createNodes(currencies, canvas) {
        const nodes = {};
        const centerX = canvas.width / 2;
        const centerY = canvas.height / 2;
        const radius = Math.min(canvas.width, canvas.height) * 0.35;

        currencies.forEach((curr, i) => {
            const angle = (i / currencies.length) * Math.PI * 2 - Math.PI / 2;
            nodes[curr] = {
                x: centerX + Math.cos(angle) * radius * this.zoom + this.pan.x,
                y: centerY + Math.sin(angle) * radius * this.zoom + this.pan.y,
                isCrypto: !['USD', 'EUR', 'GBP', 'JPY', 'AUD', 'CAD', 'CHF'].includes(curr)
            };
        });

        return nodes;
    }

    drawNodes(ctx, nodes, currencies) {
        currencies.forEach(curr => {
            const node = nodes[curr];

            // Desenhar círculo
            ctx.beginPath();
            ctx.arc(node.x, node.y, 25, 0, Math.PI * 2);
            ctx.fillStyle = node.isCrypto ? '#6366f1' : '#10b981';
            ctx.fill();
            ctx.strokeStyle = '#ffffff';
            ctx.lineWidth = 2;
            ctx.stroke();

            // Desenhar texto
            ctx.fillStyle = '#ffffff';
            ctx.font = 'bold 12px Inter';
            ctx.textAlign = 'center';
            ctx.textBaseline = 'middle';
            ctx.fillText(curr, node.x, node.y);
        });
    }

    drawOpportunityPaths(ctx, nodes, opportunities) {
        opportunities.forEach((opp, index) => {
            const opacity = 1 - (index * 0.3);
            const path = opp.path;

            for (let i = 0; i < path.length - 1; i++) {
                const from = nodes[path[i]];
                const to = nodes[path[i + 1]];

                if (from && to) {
                    ctx.beginPath();
                    ctx.moveTo(from.x, from.y);
                    ctx.lineTo(to.x, to.y);
                    ctx.strokeStyle = `rgba(245, 158, 11, ${opacity})`;
                    ctx.lineWidth = 3;
                    ctx.stroke();

                    // Desenhar seta
                    this.drawArrow(ctx, from.x, from.y, to.x, to.y, opacity);
                }
            }
        });
    }

    drawArrow(ctx, fromX, fromY, toX, toY, opacity) {
        const angle = Math.atan2(toY - fromY, toX - fromX);
        const headLength = 10;

        ctx.beginPath();
        ctx.moveTo(
            toX - headLength * Math.cos(angle - Math.PI / 6),
            toY - headLength * Math.sin(angle - Math.PI / 6)
        );
        ctx.lineTo(toX, toY);
        ctx.lineTo(
            toX - headLength * Math.cos(angle + Math.PI / 6),
            toY - headLength * Math.sin(angle + Math.PI / 6)
        );
        ctx.strokeStyle = `rgba(245, 158, 11, ${opacity})`;
        ctx.lineWidth = 2;
        ctx.stroke();
    }

    sortOpportunities() {
        // Implementar diferentes modos de ordenação
        console.log('Sort clicked - implementar diferentes ordenações');
    }

    updateStatus(status) {
        if (status === 'online') {
            this.statusBadge.style.background = 'rgba(16, 185, 129, 0.1)';
            this.statusBadge.style.borderColor = '#10b981';
            this.statusText.textContent = 'Online';
            this.statusText.style.color = '#10b981';
        } else {
            this.statusBadge.style.background = 'rgba(239, 68, 68, 0.1)';
            this.statusBadge.style.borderColor = '#ef4444';
            this.statusText.textContent = 'Offline';
            this.statusText.style.color = '#ef4444';
        }
    }

    startAutoUpdate() {
        setInterval(() => {
            this.loadData();
        }, this.updateInterval);
    }
}

// Inicializar app quando DOM estiver pronto
document.addEventListener('DOMContentLoaded', () => {
    window.app = new ArbitrageApp();
});
