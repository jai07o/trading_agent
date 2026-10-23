// BharatTrader AI — Advanced Multi-Market Controller
let ws = null;
let pnlBarChart = null;
let equityLineChart = null;
let currentState = null;
let selectedTicker = "TATASTEEL.NS";

// Helper for Indian Currency Formatting (e.g. ₹1,25,000.00)
function formatINR(number) {
    if (number === undefined || number === null || isNaN(number)) return "₹0.00";
    const sign = number < 0 ? "-" : "";
    const absVal = Math.abs(number).toFixed(2);
    const parts = absVal.split(".");
    let intPart = parts[0];
    const decPart = parts[1];

    if (intPart.length > 3) {
        const last3 = intPart.substring(intPart.length - 3);
        const otherNumbers = intPart.substring(0, intPart.length - 3);
        intPart = otherNumbers.replace(/\B(?=(\d{2})+(?!\d))/g, ",") + "," + last3;
    }
    return `${sign}₹${intPart}.${decPart}`;
}

// Initialize Charts
function initCharts() {
    // 1. P&L Bar Chart (Profits vs Suppressed Losses)
    const ctxBar = document.getElementById('pnlBarChart').getContext('2d');
    pnlBarChart = new Chart(ctxBar, {
        type: 'bar',
        data: {
            labels: [],
            datasets: [{
                label: 'Trade P&L (₹ INR)',
                data: [],
                backgroundColor: [],
                borderRadius: 4
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: { display: false },
                tooltip: {
                    callbacks: {
                        label: function(context) {
                            return `P&L: ${formatINR(context.raw)}`;
                        }
                    }
                }
            },
            scales: {
                x: {
                    grid: { color: 'rgba(255, 255, 255, 0.05)' },
                    ticks: { color: '#64748B', font: { size: 10 } }
                },
                y: {
                    grid: { color: 'rgba(255, 255, 255, 0.08)' },
                    ticks: {
                        color: '#64748B',
                        callback: function(val) { return '₹' + val; }
                    }
                }
            }
        }
    });

    // 2. Cumulative Equity Growth Curve
    const ctxLine = document.getElementById('equityLineChart').getContext('2d');
    equityLineChart = new Chart(ctxLine, {
        type: 'line',
        data: {
            labels: [],
            datasets: [{
                label: 'Portfolio Equity (₹)',
                data: [],
                borderColor: '#D4AF37',
                backgroundColor: 'rgba(212, 175, 55, 0.08)',
                borderWidth: 2,
                fill: true,
                tension: 0.35,
                pointRadius: 2,
                pointBackgroundColor: '#F59E0B'
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: { display: false },
                tooltip: {
                    callbacks: {
                        label: function(context) {
                            return `Value: ${formatINR(context.raw)}`;
                        }
                    }
                }
            },
            scales: {
                x: {
                    grid: { color: 'rgba(255, 255, 255, 0.04)' },
                    ticks: { color: '#64748B', font: { size: 10 }, maxTicksLimit: 6 }
                },
                y: {
                    grid: { color: 'rgba(255, 255, 255, 0.06)' },
                    ticks: {
                        color: '#64748B',
                        callback: function(val) { return '₹' + val.toLocaleString('en-IN'); }
                    }
                }
            }
        }
    });
}

// WebSocket Connection
function connectWebSocket() {
    const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
    const wsUrl = `${protocol}//${window.location.host}/ws`;

    ws = new WebSocket(wsUrl);

    ws.onopen = () => {
        console.log("Connected to BharatTrader AI real-time stream");
        document.getElementById("marketDot").style.background = "#10B981";
    };

    ws.onmessage = (event) => {
        const state = JSON.parse(event.data);
        currentState = state;
        updateUI(state);
    };

    ws.onclose = () => {
        console.warn("WebSocket disconnected. Reconnecting in 2 seconds...");
        document.getElementById("marketDot").style.background = "#EF4444";
        setTimeout(connectWebSocket, 2000);
    };

    ws.onerror = (err) => {
        console.error("WebSocket error:", err);
    };
}

// Update Full UI from State
function updateUI(state) {
    if (!state) return;

    // Header updates
    if (state.market_clock) {
        document.getElementById("istTime").innerText = state.market_clock.current_time;
        document.getElementById("marketSession").innerText = state.market_clock.session;
    }

    if (state.trading_mode) {
        document.getElementById("tradingModeBadge").innerText = `${state.trading_mode} SIMULATOR`;
    }

    // Autopilot toggle UI
    const toggleBtn = document.getElementById("autopilotToggleBtn");
    const toggleText = document.getElementById("autopilotText");
    if (state.autopilot_enabled) {
        toggleBtn.classList.remove("disabled");
        toggleText.innerText = "AUTONOMOUS TRADING: ON";
    } else {
        toggleBtn.classList.add("disabled");
        toggleText.innerText = "AUTONOMOUS TRADING: PAUSED";
    }

    // KPI Cards
    if (state.account_summary) {
        document.getElementById("portfolioValue").innerText = formatINR(state.account_summary.portfolio_value);
        const retSign = state.account_summary.total_return_pct >= 0 ? "+" : "";
        document.getElementById("portfolioReturn").innerText = `${retSign}${state.account_summary.total_return_pct.toFixed(2)}% Net Return`;
        
        document.getElementById("realizedPnl").innerText = formatINR(state.account_summary.realized_pnl_inr);
        document.getElementById("pnlBreakdown").innerText = `Cash: ${formatINR(state.account_summary.available_cash)}`;
    }

    if (state.loss_suppression) {
        document.getElementById("suppressedLosses").innerText = formatINR(state.loss_suppression.total_losses_suppressed_inr);
        document.getElementById("suppressedCount").innerText = `${state.loss_suppression.suppression_count} Disasters Suppressed`;
        document.getElementById("lockedProfits").innerText = formatINR(state.loss_suppression.total_profits_locked_inr);
    }

    if (state.performance) {
        document.getElementById("winRate").innerText = `${state.performance.win_rate_pct}%`;
        document.getElementById("tradeRatio").innerText = `${state.performance.winning_trades} Wins / ${state.performance.losing_trades} Losses (PF: ${state.performance.profit_factor})`;
    }

    // Daily Briefing
    if (state.daily_brief) {
        document.getElementById("dailyBriefDate").innerText = state.daily_brief.date;
        document.getElementById("morningBriefText").innerText = state.daily_brief.morning_brief;
        renderSectorHeatmap(state.daily_brief.sector_heatmap);
    }

    // Update Charts
    updateCharts(state);

    // Update Specialized Market Tables (Mining & Commodities)
    updateMiningTable(state.metals_and_mining);
    updateCommoditiesTable(state.mcx_commodities);

    // Update Positions & Trades Tables
    updatePositionsTable(state.open_positions);
    updateTradesTable(state.recent_trades);

    // Strategy Pool
    updateStrategyPool(state.strategy_pool);

    // Autonomous Self-Learning Ledger
    updateLearnedRules(state.self_learning);

    // Update Comprehensive Trading Datasets Vault UI
    updateDatasetRepositoryUI(state.dataset_repository);

    // Update Project Apex: Global Markets, Disagreement, Execution & Kill-Switch
    updateProjectApexUI(state);

    // Update Agent Scanner
    renderAgentVerdict(selectedTicker);

    // Update Suppression Log & Console
    updateSuppressionAudit(state.loss_suppression ? state.loss_suppression.recent_events : []);
    updateConsole(state.system_logs);

    // Update Real-Time Notification Center
    if (state.notifications) {
        renderNotifications(state.notifications);
    }

    // Update Universal Strategy Training Matrix
    if (state.universal_matrix) {
        const m = state.universal_matrix;
        const winEl = document.getElementById("matrixTrainedWinRate");
        const pfEl = document.getElementById("matrixProfitFactor");
        const totEl = document.getElementById("matrixTotalCount");
        if (winEl) winEl.textContent = `${m.overall_win_rate}%`;
        if (pfEl) pfEl.textContent = `${m.overall_profit_factor}`;
        if (totEl) totEl.textContent = `${m.total_strategies} Models`;
    }
}

// Render Sector Heatmap Pills
function renderSectorHeatmap(heatmap) {
    const row = document.getElementById("sectorHeatmapRow");
    if (!heatmap) return;
    let html = "";
    heatmap.forEach(s => {
        const isUp = s.change_pct >= 0;
        const color = isUp ? "#10B981" : "#EF4444";
        html += `
            <div style="background: #141926; border: 1px solid var(--border-color); padding: 5px 10px; border-radius: 6px; font-size: 11px;">
                <span style="color: var(--text-muted);">${s.name}:</span>
                <strong style="color: ${color}; margin-left: 4px;">${isUp ? "+" : ""}${s.change_pct}%</strong>
            </div>
        `;
    });
    row.innerHTML = html;
}

// Update Mining & Metals Table
function updateMiningTable(miningData) {
    const tbody = document.getElementById("miningTableBody");
    if (!miningData || miningData.length === 0) return;

    let html = "";
    miningData.forEach(m => {
        const badge = m.stance === "BULLISH" ? `<span class="badge-win">BULLISH</span>` : `<span class="badge-loss">BEARISH</span>`;
        html += `
            <tr>
                <td><strong>${m.symbol.replace(".NS", "")}</strong></td>
                <td><span style="font-size: 11px; color: var(--text-muted);">${m.underlying_commodity}</span></td>
                <td class="mono-text">${formatINR(m.current_price)}</td>
                <td class="mono-text" style="color: var(--gold-bright); font-weight: 600;">${m.mining_score}/100</td>
                <td>${badge}</td>
                <td><button class="btn-buy" style="padding: 3px 8px; font-size: 10px;" onclick="quickTrade('${m.symbol}')">Trade</button></td>
            </tr>
        `;
    });
    tbody.innerHTML = html;
}

// Update MCX Commodities Table
function updateCommoditiesTable(commData) {
    const tbody = document.getElementById("commoditiesTableBody");
    if (!commData || commData.length === 0) return;

    let html = "";
    commData.forEach(c => {
        const badge = c.stance === "BULLISH" ? `<span class="badge-win">BULLISH</span>` : `<span class="badge-loss">BEARISH</span>`;
        html += `
            <tr>
                <td><strong>${c.name}</strong></td>
                <td class="mono-text" style="color: var(--gold-bright);"><strong>${formatINR(c.price)}</strong></td>
                <td style="font-size: 11px; color: var(--text-muted);">${c.unit}</td>
                <td class="mono-text">${c.lot_size}</td>
                <td class="mono-text">${c.commodity_score}/100</td>
                <td>${badge}</td>
            </tr>
        `;
    });
    tbody.innerHTML = html;
}

// Strategy Pool
function updateStrategyPool(pool) {
    const list = document.getElementById("strategyPoolList");
    if (!pool || pool.length === 0) return;

    let html = "";
    pool.forEach((s, idx) => {
        html += `
            <div style="background: #0B0E17; border: 1px solid var(--border-color); padding: 8px 12px; border-radius: 6px; display: flex; justify-content: space-between; align-items: center; font-size: 11px;">
                <div>
                    <span style="color: var(--gold-bright); font-weight: 600;">#${idx + 1}</span> <strong>${s.name}</strong>
                </div>
                <div class="mono-text" style="color: #34D399; font-weight: 600;">Sharpe: ${s.sharpe}</div>
            </div>
        `;
    });
    list.innerHTML = html;
}

// Autonomous Self-Learning Ledger
function updateLearnedRules(selfLearning) {
    const list = document.getElementById("learnedRulesList");
    if (!selfLearning || !selfLearning.recent_insights) return;

    let html = "";
    selfLearning.recent_insights.slice().reverse().forEach((rule, idx) => {
        const isWin = rule.includes("WIN");
        const color = isWin ? "#34D399" : "#FBBF24";
        const icon = isWin ? "📈" : "🛡️";
        html += `
            <div style="background: #0B0E17; border-left: 2px solid ${color}; padding: 6px 10px; border-radius: 4px; font-size: 11px; line-height: 1.4;">
                <span style="color: ${color}; font-weight: 600;">${icon} Lesson:</span> ${rule}
            </div>
        `;
    });
    list.innerHTML = html;
}

// Update Charts Function
function updateCharts(state) {
    if (state.bar_chart_data && pnlBarChart) {
        pnlBarChart.data.labels = state.bar_chart_data.labels;
        pnlBarChart.data.datasets[0].data = state.bar_chart_data.values;
        pnlBarChart.data.datasets[0].backgroundColor = state.bar_chart_data.colors;
        pnlBarChart.update('none');
    }

    if (state.equity_curve && equityLineChart) {
        equityLineChart.data.labels = state.equity_curve.map(e => e.time);
        equityLineChart.data.datasets[0].data = state.equity_curve.map(e => e.value);
        equityLineChart.update('none');
    }
}

// Update Active Positions Table
function updatePositionsTable(positions) {
    const tbody = document.getElementById("positionsTableBody");
    document.getElementById("openCount").innerText = positions ? positions.length : 0;

    if (!positions || positions.length === 0) {
        tbody.innerHTML = `<tr><td colspan="8" class="empty-state">No open positions. Auto-Pilot is scanning high-probability setups...</td></tr>`;
        return;
    }

    let html = "";
    positions.forEach(pos => {
        const pnlClass = pos.pnl_inr >= 0 ? "emerald-text" : "crimson-text";
        html += `
            <tr>
                <td><strong>${pos.symbol.replace(".NS", "")}</strong></td>
                <td><span class="badge-win">${pos.side}</span></td>
                <td class="mono-text">${pos.quantity}</td>
                <td class="mono-text">${formatINR(pos.entry_price)}</td>
                <td class="mono-text">${formatINR(pos.current_price)}</td>
                <td class="mono-text ${pnlClass}"><strong>${formatINR(pos.pnl_inr)}</strong></td>
                <td class="mono-text ${pnlClass}">${pos.pnl_pct >= 0 ? "+" : ""}${pos.pnl_pct}%</td>
                <td><button class="btn-close" onclick="closePosition('${pos.symbol}')">Cut/Exit</button></td>
            </tr>
        `;
    });
    tbody.innerHTML = html;
}

// Update Completed Trades Table
function updateTradesTable(trades) {
    const tbody = document.getElementById("tradesTableBody");
    if (!trades || trades.length === 0) {
        tbody.innerHTML = `<tr><td colspan="8" class="empty-state">No completed trades yet. Trades will appear here automatically.</td></tr>`;
        return;
    }

    let html = "";
    trades.slice().reverse().forEach(t => {
        const badge = t.pnl_inr >= 0 ? `<span class="badge-win">WIN</span>` : `<span class="badge-loss">SUPPRESSED</span>`;
        const pnlColor = t.pnl_inr >= 0 ? "emerald-text" : "crimson-text";
        html += `
            <tr>
                <td>${t.exit_time}</td>
                <td><strong>${t.symbol.replace(".NS", "")}</strong></td>
                <td>${t.side}</td>
                <td class="mono-text">${t.quantity}</td>
                <td class="mono-text">${formatINR(t.entry_price)}</td>
                <td class="mono-text">${formatINR(t.exit_price)}</td>
                <td class="mono-text ${pnlColor}"><strong>${formatINR(t.pnl_inr)}</strong></td>
                <td>${badge}</td>
            </tr>
        `;
    });
    tbody.innerHTML = html;
}

// Render Multi-Agent Verdict
function renderAgentVerdict(ticker) {
    selectedTicker = ticker;
    if (!currentState || !currentState.watchlist_analysis) return;

    const analysis = currentState.watchlist_analysis.find(a => a.symbol === ticker);
    if (!analysis) return;

    document.getElementById("verdictSymbol").innerText = ticker;
    const actionEl = document.getElementById("verdictAction");
    actionEl.innerText = `${analysis.action} (Confidence: ${analysis.confidence}%)`;
    
    if (analysis.action === "BUY") {
        actionEl.style.color = "#10B981";
    } else if (analysis.action === "SELL") {
        actionEl.style.color = "#EF4444";
    } else {
        actionEl.style.color = "#94A3B8";
    }

    document.getElementById("fusedScore").innerText = `${analysis.fused_score}/100`;
    document.getElementById("verdictSummary").innerText = analysis.summary;

    const reports = analysis.sub_agent_reports;
    if (reports) {
        document.getElementById("agentTrendVal").innerText = `${reports.technicals.trend} (RSI: ${reports.technicals.indicators.rsi})`;
        document.getElementById("agentBullVal").innerText = `${reports.bull_analyst.confidence}% Confidence`;
        document.getElementById("agentBearVal").innerText = `Risk: ${reports.bear_analyst.risk_level}`;
        document.getElementById("agentPcrVal").innerText = `PCR: ${reports.sentiment.pcr} (${reports.sentiment.sentiment_label})`;
    }

    // Render Detected Chart Patterns (Ups & Downs)
    renderDetectedPatterns(analysis.chart_patterns);
}

function renderDetectedPatterns(patterns) {
    const list = document.getElementById("detectedPatternsList");
    const badge = document.getElementById("patternCountBadge");
    if (!list) return;

    if (!patterns || patterns.length === 0) {
        list.innerHTML = `<div class="empty-state" style="padding: 10px;">Scanning candlestick geometries and Smart Money imbalances...</div>`;
        if (badge) badge.innerText = "0 PATTERNS";
        return;
    }

    if (badge) badge.innerText = `${patterns.length} DETECTED`;
    let html = "";
    patterns.forEach(p => {
        const isBull = p.direction === "BULLISH_UP";
        const color = isBull ? "#10B981" : "#EF4444";
        const arrow = isBull ? "🟢 ⬆️ UP" : "🔴 ⬇️ DOWN";
        html += `
            <div style="background: #0A0D15; border-left: 3px solid ${color}; padding: 6px 10px; border-radius: 4px; font-size: 11px;">
                <div style="display: flex; justify-content: space-between; align-items: center;">
                    <strong>${p.pattern}</strong>
                    <span style="color: ${color}; font-weight: 700; font-size: 10px;">${arrow} (${p.confidence}%)</span>
                </div>
                <div style="color: var(--text-muted); font-size: 10px; margin-top: 2px;">
                    Target: <strong class="mono-text" style="color: ${color};">${formatINR(p.projected_target)}</strong> | Stop: <strong class="mono-text" style="color: var(--crimson);">${formatINR(p.invalidation_stop)}</strong>
                </div>
                <div style="color: var(--text-secondary); font-size: 10px; margin-top: 2px; font-style: italic;">
                    ${p.description}
                </div>
            </div>
        `;
    });
    list.innerHTML = html;
}

// Update Suppression Audit Feed
function updateSuppressionAudit(events) {
    const list = document.getElementById("suppressionLogList");
    if (!events || events.length === 0) {
        list.innerHTML = `<div class="empty-state">Loss suppression guard active. Every tick is checked in fractions of a second.</div>`;
        return;
    }

    let html = "";
    events.slice().reverse().forEach(ev => {
        const isSuppressed = ev.action === "SUPPRESS_LOSS";
        const entryClass = isSuppressed ? "suppressed" : "locked";
        const icon = isSuppressed ? "🛡️" : "💰";
        html += `
            <div class="audit-entry ${entryClass}">
                <div>
                    <strong>${icon} ${ev.symbol.replace(".NS", "")}</strong>: ${ev.reason}
                </div>
                <div class="mono-text" style="color: ${isSuppressed ? '#F59E0B' : '#10B981'}">
                    ${isSuppressed ? `Saved: ${formatINR(ev.saved_loss_inr)}` : `P&L: ${ev.pnl_pct}%`}
                </div>
            </div>
        `;
    });
    list.innerHTML = html;
}

// Update Console Telemetry
function updateConsole(logs) {
    const box = document.getElementById("consoleBox");
    if (!logs) return;

    let html = "";
    logs.slice(-25).forEach(l => {
        const lvlClass = l.level.toLowerCase();
        html += `<div class="log-line ${lvlClass}">[${l.time}] [${l.level}] ${l.message}</div>`;
    });
    box.innerHTML = html;
    box.scrollTop = box.scrollHeight;
}

// User Actions
async function toggleAutopilot() {
    if (!currentState) return;
    const newState = !currentState.autopilot_enabled;
    await fetch("/api/autopilot/toggle", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ enabled: newState })
    });
}

async function closePosition(symbol) {
    if (confirm(`Emergency Close position for ${symbol}?`)) {
        await fetch("/api/trade/close", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ symbol: symbol })
        });
    }
}

async function triggerManualBuy() {
    await fetch("/api/trade/buy", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ symbol: selectedTicker, quantity: 1 })
    });
}

async function quickTrade(symbol) {
    await fetch("/api/trade/buy", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ symbol: symbol, quantity: 1 })
    });
}

async function changeSensitivity(mode) {
    await fetch("/api/suppressor/sensitivity", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ mode: mode })
    });
}

// 20-Agent Micro Swarm Trigger
async function triggerSwarmSim() {
    const res = await fetch("/api/swarm/simulate", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ symbol: selectedTicker, score: 75.0 })
    });
    const data = await res.json();
    alert(`20-AGENT SWARM SIMULATION FOR ${data.symbol}:\nConsensus: ${data.swarm_consensus}\nBuy: ${data.buy_pct}%\nSell: ${data.sell_pct}%\nHold: ${data.hold_pct}%\nConviction: ${data.liquidity_conviction}`);
}

// What-If Scenario Trigger
async function runWhatIfSimulation() {
    const scenario = document.getElementById("whatifSelect").value;
    const res = await fetch("/api/whatif/simulate", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ scenario: scenario })
    });
    const data = await res.json();
    
    let html = `<strong>${data.scenario}</strong><br><span style="color: var(--text-muted);">${data.impact_summary}</span><br><br>`;
    data.projected_asset_movements.forEach(m => {
        const col = m.projected_move_pct >= 0 ? '#10B981' : '#EF4444';
        html += `• <strong>${m.symbol}</strong>: <span style="color: ${col}; font-weight: 600;">${m.projected_move_pct > 0 ? '+' : ''}${m.projected_move_pct}%</span> (${m.direction}) [${m.loss_suppression_status}]<br>`;
    });
    html += `<br><span style="color: var(--gold-bright);">🛡️ ${data.loss_suppression_verdict}</span>`;
    document.getElementById("whatifResultBox").innerHTML = html;
}

// Update Comprehensive Trading Datasets Vault UI
function updateDatasetRepositoryUI(repoStats) {
    if (!repoStats) return;
    const badge = document.getElementById("datasetHealthBadge");
    const totalEl = document.getElementById("datasetTotalCount");
    const entitiesEl = document.getElementById("datasetEntitiesCount");
    const miningEl = document.getElementById("datasetMiningCount");
    const patternEl = document.getElementById("datasetPatternCount");

    if (badge && repoStats.dataset_health) badge.textContent = "100% SYNCHRONIZED";
    if (totalEl && repoStats.total_datasets_indexed) totalEl.textContent = `${repoStats.total_datasets_indexed} Datasets`;
    if (entitiesEl && repoStats.total_data_entities) entitiesEl.textContent = `${repoStats.total_data_entities} Entities`;
    if (miningEl && repoStats.mining_corporations_indexed) miningEl.textContent = `${repoStats.mining_corporations_indexed} Reserves`;
    if (patternEl && repoStats.patterns_calibrated) patternEl.textContent = `${repoStats.patterns_calibrated} Calibrated`;
}

// Quick Category Inspector for Datasets
async function inspectDatasetCategory(category) {
    const box = document.getElementById("datasetOutputBox");
    box.innerHTML = `<span style="color: #A78BFA;">Fetching dataset for ${category}...</span>`;
    
    try {
        let endpoint = `/api/datasets/${category}`;
        if (category === "macro") endpoint = "/api/datasets/macro";
        
        const res = await fetch(endpoint);
        const data = await res.json();
        
        let formatted = "";
        if (category === "microstructure") {
            formatted = `<strong>⚖️ SEBI STT & STATUTORY CHARGES (INDIA):</strong><br>`;
            const charges = data.statutory_charges_schedule_inr || {};
            for (let k in charges) {
                formatted += `• <strong>${k.toUpperCase()}</strong>: STT: ${charges[k].stt_rate || 'N/A'} | Exch: ${charges[k].exchange_turnover_fee_nse || charges[k].exchange_turnover_charges || 'N/A'}<br>`;
            }
        } else if (category === "patterns") {
            formatted = `<strong>📐 UNIVERSAL TECHNICAL & CHART PATTERN STATISTICS:</strong><br>`;
            for (let p in data) {
                formatted += `• <strong>${p}</strong>: Win Rate: <span style="color: #34D399; font-weight: 600;">${data[p].win_rate_pct}%</span> | Profit Factor: ${data[p].profit_factor} | RR: ${data[p].avg_risk_reward}<br>`;
            }
        } else if (category === "mining") {
            formatted = `<strong>⛏️ INDIAN MINING CORPORATIONS & RESERVES:</strong><br>`;
            const corps = data.mining_corporations || {};
            for (let c in corps) {
                formatted += `• <strong>${corps[c].company_name || c}</strong> (${corps[c].symbol}): ${corps[c].global_rank || corps[c].ownership || ''} | Production: ${corps[c].annual_production_mt || ''} MT<br>`;
            }
        } else if (category === "macro") {
            formatted = `<strong>🏦 RBI POLICY CYCLES & INSTITUTIONAL FLOWS:</strong><br>`;
            const rbi = data.rbi_monetary_policy_cycles || [];
            rbi.forEach(cycle => {
                formatted += `• Year ${cycle.year}: Repo Rate ${cycle.repo_rate_pct}% (${cycle.stance}) → Impact: ${cycle.market_reaction}<br>`;
            });
        } else if (category === "fundamentals") {
            formatted = `<strong>🏢 CORPORATE VALUATIONS & NIFTY WEIGHTS:</strong><br>`;
            const fund = data.fundamentals || {};
            for (let s in fund) {
                formatted += `• <strong>${s}</strong>: P/E: ${fund[s].pe_ratio} | P/B: ${fund[s].pb_ratio} | ROE: ${fund[s].roe_pct}% | Thesis: ${fund[s].core_thesis}<br>`;
            }
        } else if (category === "forex-crypto") {
            formatted = `<strong>💱 FOREX CROSSES & VDA TAX COMPLIANCE:</strong><br>`;
            const crosses = data.forex_currency_crosses || {};
            for (let cx in crosses) {
                formatted += `• <strong>${crosses[cx].pair}</strong>: Range: [${crosses[cx].typical_range ? crosses[cx].typical_range.join(' - ') : 'N/A'}] | Sensitivity: ${crosses[cx].fii_equity_sensitivity || crosses[cx].trade_impact || ''}<br>`;
            }
        }
        box.innerHTML = formatted || JSON.stringify(data, null, 2);
    } catch (err) {
        box.innerHTML = `<span style="color: #EF4444;">Error inspecting dataset: ${err.message}</span>`;
    }
}

// Deep Search Across All Datasets
async function searchDataset() {
    const input = document.getElementById("datasetSearchInput");
    const query = input.value.trim();
    if (!query) return;
    
    const box = document.getElementById("datasetOutputBox");
    box.innerHTML = `<span style="color: #A78BFA;">Searching vault for "${query}"...</span>`;
    
    try {
        const res = await fetch(`/api/datasets/search?q=${encodeURIComponent(query)}`);
        const data = await res.json();
        
        if (!data.results || data.results.length === 0) {
            box.innerHTML = `<span style="color: var(--text-muted);">No direct matches found for "${query}". Try searching "STT", "CIL", "Repo", "W-Pattern", "Zinc", or "NMDC".</span>`;
            return;
        }
        
        let html = `<strong>🔍 SEARCH RESULTS FOR "${query.toUpperCase()}":</strong><br>`;
        data.results.forEach(r => {
            html += `• <strong>${r.dataset_category.toUpperCase()} DATASET</strong>: Matched empirical data points found.<br>`;
        });
        box.innerHTML = html;
    } catch (err) {
        box.innerHTML = `<span style="color: #EF4444;">Search failed: ${err.message}</span>`;
    }
}

// Project Apex: Global Market Intelligence, Execution & Kill-Switch UI Updater
function updateProjectApexUI(state) {
    if (!state) return;

    // 1. Cross-Market Relationship Graph & Macro Regime
    if (state.cross_market_graph) {
        const regimeBadge = document.getElementById("apexRegimeBadge");
        const macroSummary = document.getElementById("apexMacroSummary");
        if (regimeBadge) {
            regimeBadge.textContent = state.cross_market_graph.regime.replace(/_/g, " ");
            if (state.cross_market_graph.regime === "GLOBAL_RISK_ON") {
                regimeBadge.style.color = "#34D399";
                regimeBadge.style.background = "rgba(16, 185, 129, 0.15)";
            } else if (state.cross_market_graph.regime === "GLOBAL_RISK_OFF") {
                regimeBadge.style.color = "#EF4444";
                regimeBadge.style.background = "rgba(239, 68, 68, 0.15)";
            } else {
                regimeBadge.style.color = "#F59E0B";
                regimeBadge.style.background = "rgba(245, 158, 11, 0.15)";
            }
        }
        if (macroSummary) {
            macroSummary.textContent = state.cross_market_graph.regime_summary;
        }
    }

    // 2. Model Disagreement & Epistemic Uncertainty
    if (state.watchlist_analysis && state.watchlist_analysis.length > 0) {
        const activeItem = state.watchlist_analysis.find(i => i.symbol === selectedTicker) || state.watchlist_analysis[0];
        const disagreement = activeItem.model_disagreement;
        const diagVerdict = document.getElementById("apexDisagreementVerdict");
        const diagStats = document.getElementById("apexDisagreementStats");

        if (disagreement && diagVerdict) {
            if (disagreement.policy_action === "FULL_CONSENSUS") {
                diagVerdict.textContent = "Full Consensus (100% Size)";
                diagVerdict.style.color = "#34D399";
            } else if (disagreement.policy_action === "DERISK_HALF_SIZE") {
                diagVerdict.textContent = "Divergence Detected (50% De-Risk)";
                diagVerdict.style.color = "#F59E0B";
            } else {
                diagVerdict.textContent = "Mandatory Abstain (High Conflict)";
                diagVerdict.style.color = "#EF4444";
            }
        }
        if (disagreement && diagStats) {
            diagStats.textContent = `MDI: ${disagreement.disagreement_index} · Uncertainty: ${disagreement.uncertainty_pct}%`;
        }
    }

    // 3. Execution Quality Optimizer
    if (state.execution_optimizer) {
        const gradeEl = document.getElementById("apexExecutionGrade");
        const latencyEl = document.getElementById("apexLatencyStats");
        if (gradeEl) {
            gradeEl.textContent = state.execution_optimizer.overall_grade.replace(/_/g, " ");
        }
        if (latencyEl) {
            latencyEl.textContent = `Latency: ${state.execution_optimizer.avg_execution_latency_ms}ms · Slippage: ${state.execution_optimizer.avg_slippage_bps > 0 ? '+' : ''}${state.execution_optimizer.avg_slippage_bps} bps`;
        }
    }

    // 4. Automated Research Laboratory
    if (state.research_lab) {
        const labStatus = document.getElementById("apexLabStatus");
        if (labStatus) {
            labStatus.textContent = `${state.research_lab.strategies_promoted_count} Promoted · ${state.research_lab.strategies_rejected_count} Filtered`;
        }
    }

    // 5. Independent Kill-Switch & Risk Guardian
    if (state.risk_guardian) {
        const killBtn = document.getElementById("panicKillSwitchBtn");
        const killText = document.getElementById("killSwitchText");
        if (state.risk_guardian.kill_switch_state === "ARMED_AND_ACTIVE") {
            if (killText) killText.textContent = "KILL-SWITCH: ARMED";
            if (killBtn) {
                killBtn.style.background = "rgba(220, 38, 38, 0.2)";
                killBtn.style.borderColor = "#DC2626";
                killBtn.style.color = "#FCA5A5";
            }
        } else {
            if (killText) killText.textContent = "⚠️ TRADING HALTED (RESET)";
            if (killBtn) {
                killBtn.style.background = "#DC2626";
                killBtn.style.borderColor = "#EF4444";
                killBtn.style.color = "#FFFFFF";
                killBtn.style.animation = "pulse 1.5s infinite";
            }
        }
    }
}

// Emergency Panic Kill-Switch Toggle
async function toggleKillSwitch() {
    if (!currentState || !currentState.risk_guardian) return;
    const isArmed = (currentState.risk_guardian.kill_switch_state === "ARMED_AND_ACTIVE");

    if (isArmed) {
        const confirmHalt = confirm("⚠️ EMERGENCY STOP CONFIRMATION:\n\nTrigger independent hardware-level Kill-Switch?\nThis will immediately halt all new orders and block algorithmic execution.");
        if (!confirmHalt) return;

        await fetch("/api/apex/kill-switch/trigger", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ reason: "User triggered Emergency Panic Halt from Dashboard." })
        });
    } else {
        await fetch("/api/apex/kill-switch/reset", {
            method: "POST",
            headers: { "Content-Type": "application/json" }
        });
    }
}

// Direct Online Trading Platform Test Runner
async function fetchLiveOnlineQuote() {
    const symbol = document.getElementById("onlineTestTicker").value;
    const consoleBox = document.getElementById("onlineTestConsole");
    const badge = document.getElementById("onlineTestDurationBadge");
    
    badge.textContent = "Fetching Live Tick...";
    badge.style.color = "#F59E0B";

    consoleBox.innerHTML = `<div style="color: #60A5FA;">[NETWORK] Requesting live online market quote for ${symbol} from exchange tick bridge...</div>`;

    try {
        const res = await fetch(`/api/online/quote/${encodeURIComponent(symbol)}`);
        const data = await res.json();

        if (data.status === "SUCCESS") {
            badge.textContent = `Latency: ${data.latency_ms.toFixed(1)}ms`;
            badge.style.color = "#34D399";
            consoleBox.innerHTML = `
                <div style="color: #10B981; font-weight: 600;">[EXCHANGE TICK CONFIRMED] ${symbol}</div>
                <div style="color: #FBBF24;">-> Live Exchange Price: ₹${data.live_price.toFixed(2)}</div>
                <div style="color: #94A3B8;">-> Day High: ₹${data.day_high.toFixed(2)} | Day Low: ₹${data.day_low.toFixed(2)}</div>
                <div style="color: #94A3B8;">-> Exchange Source: ${data.source} | Feed Round-Trip: ${data.latency_ms.toFixed(1)}ms</div>
                <div style="color: #34D399;">Ready for full online trade test! Click "Run Direct Online Platform Test".</div>
            `;
        } else {
            badge.textContent = "Error";
            badge.style.color = "#EF4444";
            consoleBox.innerHTML = `<div style="color: #EF4444;">[ERROR] Failed to fetch quote: ${data.error || 'Unknown error'}</div>`;
        }
    } catch (err) {
        badge.textContent = "Network Error";
        badge.style.color = "#EF4444";
        consoleBox.innerHTML = `<div style="color: #EF4444;">[ERROR] Bridge connection failed: ${err.message}</div>`;
    }
}

async function runOnlinePlatformTest() {
    const symbol = document.getElementById("onlineTestTicker").value;
    const consoleBox = document.getElementById("onlineTestConsole");
    const badge = document.getElementById("onlineTestDurationBadge");
    const testBtn = document.getElementById("runOnlineTestBtn");

    testBtn.disabled = true;
    testBtn.style.opacity = "0.6";
    badge.textContent = "EXECUTING DIRECT ONLINE TEST...";
    badge.style.color = "#F59E0B";

    consoleBox.innerHTML = `
        <div style="color: #60A5FA;">[INIT] Starting direct online trading platform execution test for ${symbol}...</div>
        <div style="color: #94A3B8;">Connecting to online exchange tick feed, Kelly position sizer, Risk Guardian, and sub-second loss suppressor...</div>
    `;

    try {
        const res = await fetch("/api/online/test-trade", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ symbol: symbol })
        });
        const result = await res.json();

        if (result.status === "SUCCESS") {
            badge.textContent = `${result.total_test_duration_ms}ms (100% PASS)`;
            badge.style.color = "#34D399";

            let logsHtml = `<div style="color: #34D399; font-weight: 700; margin-bottom: 4px;">✅ DIRECT ONLINE PLATFORM TEST PASSED (Duration: ${result.total_test_duration_ms}ms)</div>`;
            if (result.test_logs && result.test_logs.length > 0) {
                result.test_logs.forEach(log => {
                    let color = "#94A3B8";
                    if (log.includes("Verified Live Online Price")) color = "#FBBF24";
                    else if (log.includes("Risk Guardian APPROVED")) color = "#34D399";
                    else if (log.includes("ORDER FILLED ONLINE")) color = "#60A5FA";
                    else if (log.includes("LOSS SUPPRESSION SUCCESS")) color = "#10B981";
                    else if (log.includes("SUCCESS")) color = "#34D399";
                    logsHtml += `<div style="color: ${color};">${log}</div>`;
                });
            }
            consoleBox.innerHTML = logsHtml;
        } else {
            badge.textContent = "TEST HALTED";
            badge.style.color = "#EF4444";
            consoleBox.innerHTML = `
                <div style="color: #EF4444; font-weight: 700;">❌ Test Halted at ${result.stage || 'STAGE'}: ${result.reason || 'Safety Triggered'}</div>
                <div style="color: #94A3B8;">${JSON.stringify(result)}</div>
            `;
        }
    } catch (err) {
        badge.textContent = "Test Failed";
        badge.style.color = "#EF4444";
        consoleBox.innerHTML = `<div style="color: #EF4444;">[FAIL] Direct test failed: ${err.message}</div>`;
    } finally {
        testBtn.disabled = false;
        testBtn.style.opacity = "1";
    }
}

// ==========================================
// BROWSER AUDIO CHIMES & NOTIFICATION CENTER
// ==========================================
let audioCtx = null;
let soundEnabled = true;
let lastKnownNotifId = null;

function getAudioContext() {
    if (!audioCtx) {
        const AudioContext = window.AudioContext || window.webkitAudioContext;
        if (AudioContext) audioCtx = new AudioContext();
    }
    if (audioCtx && audioCtx.state === "suspended") {
        audioCtx.resume();
    }
    return audioCtx;
}

function playChime(type) {
    if (!soundEnabled) return;
    try {
        const ctx = getAudioContext();
        if (!ctx) return;
        const now = ctx.currentTime;
        const osc = ctx.createOscillator();
        const gain = ctx.createGain();
        osc.connect(gain);
        gain.connect(ctx.destination);

        if (type === "profit") {
            // Ascending major chord (C5 -> E5 -> G5)
            osc.type = "triangle";
            osc.frequency.setValueAtTime(523.25, now);
            osc.frequency.setValueAtTime(659.25, now + 0.1);
            osc.frequency.setValueAtTime(783.99, now + 0.2);
            gain.gain.setValueAtTime(0.18, now);
            gain.gain.exponentialRampToValueAtTime(0.001, now + 0.5);
            osc.start(now);
            osc.stop(now + 0.5);
        } else if (type === "loss") {
            // Shield Defense tone (E4 -> C4)
            osc.type = "sine";
            osc.frequency.setValueAtTime(329.63, now);
            osc.frequency.setValueAtTime(261.63, now + 0.15);
            gain.gain.setValueAtTime(0.2, now);
            gain.gain.exponentialRampToValueAtTime(0.001, now + 0.45);
            osc.start(now);
            osc.stop(now + 0.45);
        } else {
            // Trade click (A5 -> C6)
            osc.type = "sine";
            osc.frequency.setValueAtTime(880.0, now);
            osc.frequency.setValueAtTime(1046.5, now + 0.08);
            gain.gain.setValueAtTime(0.15, now);
            gain.gain.exponentialRampToValueAtTime(0.001, now + 0.25);
            osc.start(now);
            osc.stop(now + 0.25);
        }
    } catch (e) {}
}

function toggleNotificationDrawer() {
    const drawer = document.getElementById("notificationDrawer");
    if (!drawer) return;
    drawer.style.display = (drawer.style.display === "none" || drawer.style.display === "") ? "flex" : "none";
}

function toggleSound(enabled) {
    soundEnabled = enabled;
}

async function saveNotificationSettings() {
    const telegramToken = document.getElementById("notifTelegramToken").value;
    const telegramChat = document.getElementById("notifTelegramChat").value;
    const discordWebhook = document.getElementById("notifDiscordWebhook").value;
    const sound = document.getElementById("notifSoundToggle").checked;

    await fetch("/api/notifications/settings", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
            telegram_token: telegramToken,
            telegram_chat: telegramChat,
            discord_webhook: discordWebhook,
            sound_enabled: sound
        })
    });
    alert("✅ Notification preferences saved! Alerts will be dispatched to configured channels.");
}

async function testNotification() {
    playChime("trade");
    const res = await fetch("/api/notifications/test", { method: "POST" });
    const data = await res.json();
    if (data.record) {
        renderNotifications([data.record]);
    }
}

async function markAllNotificationsRead() {
    await fetch("/api/notifications/mark-read", { method: "POST" });
    const badge = document.getElementById("notifBadge");
    if (badge) {
        badge.textContent = "0";
        badge.style.background = "#64748B";
    }
}

function renderNotifications(notifications) {
    const listEl = document.getElementById("notificationList");
    const badge = document.getElementById("notifBadge");
    if (!listEl) return;

    if (!notifications || notifications.length === 0) {
        listEl.innerHTML = '<div style="color: #64748B; font-size: 11px; text-align: center; padding: 12px;">No unread notifications.</div>';
        return;
    }

    const unreadCount = notifications.filter(n => !n.read).length;
    if (badge) {
        badge.textContent = unreadCount;
        badge.style.background = unreadCount > 0 ? "#10B981" : "#64748B";
    }

    // Check if newest notification is new and chime
    if (notifications.length > 0 && notifications[0].id !== lastKnownNotifId) {
        const topNotif = notifications[0];
        lastKnownNotifId = topNotif.id;
        if (topNotif.severity === "PROFIT_LOCK") playChime("profit");
        else if (topNotif.severity === "LOSS_CUT") playChime("loss");
        else if (topNotif.severity === "TRADE_FILL") playChime("trade");
    }

    let html = "";
    notifications.forEach(n => {
        let borderCol = "#3B82F6";
        let icon = "⚡";
        if (n.severity === "PROFIT_LOCK") { borderCol = "#10B981"; icon = "🔒"; }
        else if (n.severity === "LOSS_CUT") { borderCol = "#EF4444"; icon = "🛡️"; }
        else if (n.severity === "RISK_ALERT") { borderCol = "#F59E0B"; icon = "🚨"; }

        html += `
            <div style="background: #0B0E17; border-left: 3px solid ${borderCol}; border-radius: 4px; padding: 8px 10px; font-size: 11px;">
                <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 2px;">
                    <strong style="color: ${borderCol}; font-size: 11px;">${icon} ${n.title}</strong>
                    <span style="font-size: 9px; color: var(--text-muted);">${n.timestamp ? n.timestamp.split(' ')[1] : ''}</span>
                </div>
                <div style="color: var(--text-secondary); line-height: 1.3; font-size: 10px;">${n.message}</div>
            </div>
        `;
    });
    listEl.innerHTML = html;
}

// ==========================================
// TRADINGVIEW STUDIO & AI STRATEGY TRAINING
// ==========================================

async function loadPineScript() {
    try {
        const res = await fetch("/api/tradingview/pinescript");
        const data = await res.json();
        const display = document.getElementById("pineScriptDisplay");
        if (display && data.pinescript) {
            display.value = data.pinescript;
        }
    } catch (e) {}
}

function copyPineScript() {
    const display = document.getElementById("pineScriptDisplay");
    if (!display) return;
    navigator.clipboard.writeText(display.value);
    alert("✅ Official BharatTrader Pine Script strategy copied to clipboard!\n\n1. Open TradingView (website or app)\n2. Click 'Pine Editor' at the bottom\n3. Paste this script\n4. Click 'Add to chart'\n5. Set alert with Webhook URL to trade autonomously!");
}

function copyWebhookUrl() {
    const webhookUrl = `${window.location.origin}/api/webhook/tradingview`;
    navigator.clipboard.writeText(webhookUrl);
    alert(`✅ TradingView Webhook URL Copied:\n\n${webhookUrl}\n\nPaste this URL into your TradingView Alert settings under 'Webhook URL'.`);
}

async function trainAgentFromTradingView() {
    const symbol = document.getElementById("tvTrainSymbol").value;
    const btn = document.getElementById("trainAgentBtn");
    const badge = document.getElementById("tvTrainingBadge");
    const statusEl = document.getElementById("tvPromotionStatus");

    btn.disabled = true;
    btn.style.opacity = "0.6";
    badge.textContent = "TRAINING IN PROGRESS...";
    badge.style.color = "#F59E0B";
    statusEl.textContent = `Evaluating 50 hyperparameter generations on historical ${symbol} data...`;

    try {
        const res = await fetch("/api/tradingview/train", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ symbol: symbol, generations: 50 })
        });
        const result = await res.json();

        if (result.status === "PROMOTED_TO_PRODUCTION") {
            playChime("profit");
            badge.textContent = `${result.duration_ms}ms · PROMOTED`;
            badge.style.color = "#34D399";

            document.getElementById("tvWinRateBefore").textContent = `${result.win_rate_before}%`;
            document.getElementById("tvWinRateAfter").textContent = `${result.win_rate_after}% (+${result.win_rate_gain_pct}%)`;
            
            const p = result.optimal_params;
            document.getElementById("tvOptimalParams").textContent = 
                `${p.supertrend_atr} ATR (${p.supertrend_factor}x) · ${p.ema_fast}/${p.ema_slow} EMA · ${p.loss_suppress_cut_pct}% Cut · PF ${result.profit_factor_after}`;

            statusEl.innerHTML = `✅ <strong>PROMOTED:</strong> Calibrated strategy added to production evolution pool & RAG memory. Win rate elevated to <strong>${result.win_rate_after}%</strong>.`;
        }
    } catch (err) {
        badge.textContent = "Error";
        statusEl.textContent = `Training failed: ${err.message}`;
    } finally {
        btn.disabled = false;
        btn.style.opacity = "1";
    }
}

// Universal 10-Discipline Worldwide Strategy Training
async function trainAllWorldStrategies() {
    const btn = document.getElementById("trainWorldStrategiesBtn");
    const badge = document.getElementById("universalMatrixBadge");

    btn.disabled = true;
    btn.style.opacity = "0.6";
    badge.textContent = "TRAINING 10 DISCIPLINES...";
    badge.style.color = "#F59E0B";

    try {
        const res = await fetch("/api/training/universal-train-all", { method: "POST" });
        const result = await res.json();

        if (result.status === "UNIVERSAL_TRAINING_COMPLETE") {
            playChime("profit");
            badge.textContent = `${result.strategies_trained_count} STRATEGIES CALIBRATED`;
            badge.style.color = "#34D399";

            document.getElementById("matrixTrainedWinRate").textContent = `${result.overall_trained_win_rate}%`;
            document.getElementById("matrixProfitFactor").textContent = `${result.overall_trained_profit_factor}`;

            alert(`🌍 Universal Strategy Training Complete!\n\nAll 10 Global Disciplines (${result.strategies_trained_count} strategies) successfully calibrated on historical Indian & Global datasets.\n\nOverall Win Rate: ${result.overall_trained_win_rate}%\nProfit Factor: ${result.overall_trained_profit_factor}\n\nTop 6 strategies promoted to active production pool.`);
        }
    } catch (err) {
        badge.textContent = "Error";
        badge.style.color = "#EF4444";
        alert(`Training failed: ${err.message}`);
    } finally {
        btn.disabled = false;
        btn.style.opacity = "1";
    }
}

// Bootstrap on load
window.addEventListener("DOMContentLoaded", () => {
    initCharts();
    connectWebSocket();
    loadPineScript();
});

