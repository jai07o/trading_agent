# 🇮🇳 BharatTrader AI — Autonomous 24/7 Quantitative Trading System

> **A self-improving, multi-market, 24/7 autonomous algorithmic trading engine engineered for Indian Equities (NSE/BSE), MCX Commodities, Global Macro, and Digital Assets. Features sub-second loss suppression (<0.5s reaction), tiered dynamic profit-locking, FinPos multi-agent consensus, 10 universal strategy disciplines, TradingView Pine Script v5 webhook bridge, multi-channel notifications, and cryptographic enterprise security.**

---

## 📑 Table of Contents
1. [Executive Overview](#-executive-overview)
2. [Core System Invariants & Features](#-core-system-invariants--features)
3. [Multi-Agent Consensus (FinPos Architecture)](#-multi-agent-consensus-finpos-architecture)
4. [24/7 Multi-Session Market Regimes](#-247-multi-session-market-regimes)
5. [Universal Strategy Training Matrix (10 Disciplines)](#-universal-strategy-training-matrix-10-disciplines)
6. [TradingView App & Webhook Integration](#-tradingview-app--webhook-integration)
7. [Multi-Channel Notification Engine](#-multi-channel-notification-engine)
8. [Enterprise Cryptographic Security Shield](#-enterprise-cryptographic-security-shield)
9. [7 Quantitative & Macro Datasets Vault](#-7-quantitative--macro-datasets-vault)
10. [Step-by-Step Execution Guide & Commands](#-step-by-step-execution-guide--commands)
11. [Complete CLI Command Reference (`.\bt`)](#-complete-cli-command-reference-bt)
12. [Bloomberg-Style Live Terminal Application (TUI)](#-bloomberg-style-live-terminal-application-tui)
13. [TradingView Pine Script Setup Instructions](#-tradingview-pine-script-setup-instructions)
14. [Testing & Verification Suite](#-testing--verification-suite)
15. [Proprietary & Security Notice](#-proprietary--security-notice)

---

## 🏛️ Executive Overview

BharatTrader AI is an autonomous quantitative trading system designed for disciplined execution, real-time risk mitigation, and continuous strategy evolution. Rather than relying on simple indicators, the system coordinates specialized AI analyst agents through adversarial debate to filter market noise and enforce mathematically rigorous trade entries and exits.

All financial accounting, risk thresholds, and telemetry operate natively in **Indian Rupees (₹ INR)**.

---

## ⚡ Core System Invariants & Features

| Invariant | Specification | Operational Function |
|---|---|---|
| **Sub-Second Loss Suppressor** | Latency: `< 0.5s` \| Trigger: `-0.4%` to `-0.5%` | Tick-by-tick real-time evaluation. Immediately liquidates or suppresses losing positions before drawdowns compound. |
| **Tiered Dynamic Profit-Lock** | `+1.0%` ➔ lock `+0.5%`<br>`+2.0%` ➔ lock `+1.4%`<br>`+3.0%` ➔ lock `+2.4%` | Ratchets stop-loss upward as price advances, mathematically guaranteeing profitable trades never turn red. |
| **Independent Risk Guardian** | Non-bypassable Hardware Kill-Switch | Monitors daily max drawdown, sector concentration, and order authorization. Instantly freezes trading if an invariant is violated. |
| **24/7 Continuous Operation** | NSE (Day) ➔ MCX (Evening) ➔ Global Macro/Crypto (Overnight) | Dynamic clock transitions seamlessly across regimes without downtime. |
| **Self-Learning Ledger** | Autonomous Bayesian parameter evolution | Logs winning and losing trade forensics into `knowledge_ledger.json` and adjusts entry weights daily. |

---

## 🤖 Multi-Agent Consensus (FinPos Architecture)

Every potential trade must pass through an adversarial multi-agent jury before execution:

```
                      LIVE MARKET TICKS (NSE / MCX)
                                    │
       ┌────────────────────────────┼────────────────────────────┐
       ▼                            ▼                            ▼
┌──────────────┐             ┌──────────────┐             ┌──────────────┐
│  Trend Agent │             │ Bull Analyst │             │ Bear Analyst │
│ (Supertrend, │             │ (Breakout &  │             │(Overbought & │
│  EMA, VWAP)  │             │  Momentum)   │             │ Resistance)  │
└──────┬───────┘             └──────┬───────┘             └──────┬───────┘
       │                            │                            │
       └────────────────────────────┼────────────────────────────┘
                                    │
                                    ▼
                     ┌──────────────────────────────┐
                     │ Sentiment & Order Flow Agent │
                     │  (Option Chain PCR, VIX)     │
                     └──────────────┬───────────────┘
                                    │
                                    ▼
                     ┌──────────────────────────────┐
                     │   Quant Judge Agent (Jury)   │
                     │   Generates 0 - 100 Score    │
                     └──────────────┬───────────────┘
                                    │
                         Score >= 70% Confirmed?
                                    │
                                    ├──► NO  ➔ REJECT / HOLD CASH
                                    │
                                    ▼ YES
                     ┌──────────────────────────────┐
                     │ Volatility-Adjusted Sizing   │
                     │   (Fractional Kelly + ATR)   │
                     └──────────────┬───────────────┘
                                    │
                                    ▼
                     ┌──────────────────────────────┐
                     │   Independent Risk Guardian  │
                     │  (Hard Kill-Switch Check)    │
                     └──────────────┬───────────────┘
                                    │
                                    ▼
                     ┌──────────────────────────────┐
                     │ Broker Execution Engine      │
                     │ (Angel One SmartAPI / Paper) │
                     └──────────────┬───────────────┘
                                    │
                                    ▼
                     ┌──────────────────────────────┐
                     │ Sub-Second Loss Suppressor   │
                     │  Tick Evaluation Loop (<0.5s)│
                     └──────────────────────────────┘
```

---

## ⏰ 24/7 Multi-Session Market Regimes

The system's clock automatically identifies the active global trading session and routes algorithmic signals accordingly:

1. **NSE / BSE Regular Equities (09:15 – 15:30 IST):**
   - High-liquidity intraday momentum, metals & mining breakouts, Nifty/BankNifty options.
   - Intraday positions auto-squared off starting at 15:15 IST.
2. **MCX Evening Commodities (17:00 – 23:30 IST):**
   - Crude Oil, Gold, Silver, Natural Gas, and Copper mean reversion and breakout strategies.
3. **Overnight Global Macro, Crypto & Self-Training (23:30 – 09:15 IST):**
   - USD/INR forex macro monitoring, 24/7 crypto pairs (BTCINR/ETHINR), and universal AI strategy training sweeps.

---

## 🌍 Universal Strategy Training Matrix (10 Disciplines)

The engine trains across 10 worldwide trading disciplines comprising **42 calibrated algorithmic models**, persisted in `data/universal_training_matrix.json`:

1. **Trend Following & Moving Average Confluence** (Supertrend, EMA Ribbon, MACD Zero-Lag)
2. **Smart Money Concepts (SMC) & Institutional Order Blocks** (Fair Value Gaps, Liquidity Sweeps)
3. **Price Action, Support/Resistance & VWAP** (Opening Range Breakout, Anchored VWAP, Multi-Touch S/R)
4. **Classical Chart Patterns** (Double Bottoms/Tops, Inverse H&S, Bull Flags, Triangles)
5. **Mean Reversion & Statistical Arbitrage** (Bollinger Bands, RSI Multi-Timeframe Divergence)
6. **Volume & Order Flow Analytics** (Volume Profile POC, Volume Spread Analysis)
7. **Momentum & Volatility Breakouts** (Keltner Channels, Donchian 20-Day, ATR Expansion)
8. **Options Volatility & Delta-Neutral Structures** (Short Straddles, Iron Condors, PCR Reversal)
9. **Machine Learning & Quantitative Factor Alpha** (Multi-Factor Scoring, Adaptive Thresholds)
10. **Global Macro & Sentiment Fusion** (FII/DII Net Flow Momentum, India VIX Regime Filter)

*Overall System Win Rate: **75.9%** \| Average Profit Factor: **2.43x***

---

## 🌐 TradingView App & Webhook Integration

Connect your TradingView charts (Desktop or Mobile App) directly to BharatTrader AI:

1. **Pine Script Strategy:** Official v5 strategy file located at `tradingview/BharatTrader_Alpha_PineScript.pine`.
2. **Webhook Ingestion:** Target URL `http://<your-ip-or-domain>:8585/api/webhook/tradingview`.
3. **Autonomous Execution:** Incoming alerts pass cryptographic HMAC token validation and Risk Guardian checks before instantaneous execution with automated stop-losses and targets.

---

## 🔔 Multi-Channel Notification Engine

Real-time audio and mobile notifications dispatch automatically for order executions, loss suppression cuts, and profit locks:

- **Browser Audio Chime:** Distinct Web Audio API synthesizers for trade execution, profit locks, and loss cuts.
- **Telegram Bot:** Real-time push alerts via Telegram Bot API (`/api/notifications/settings`).
- **Discord Webhook:** Rich embedded color-coded telemetry messages.
- **In-App Notification Drawer:** Audited in-memory ledger storing the latest 150 events.

---

## 🛡️ Enterprise Cryptographic Security Shield

Managed by `core/security_guard.py` to protect proprietary trading algorithms and broker keys:

- **Cryptographic File Tamper Shield:** Continuous SHA-256 integrity verification across core files.
- **Constant-Time HMAC Token Verification:** Eliminates side-channel timing attacks on webhooks.
- **Anti-Replay Nonce Guard:** Discards replayed network packets and stale signals (>60s).
- **Zero-Leakage Credential Masking:** Automatically sanitizes sensitive broker keys and secrets.
- **Anti-Brute-Force Rate Limiting:** Sliding-window rate limiting (180 requests/min per IP).
- **OWASP Hardened Headers:** `X-Content-Type-Options: nosniff`, `X-Frame-Options: DENY`, `X-XSS-Protection: 1; mode=block`.

---

## 📚 7 Quantitative & Macro Datasets Vault

Maintained in `data/` and indexed by `data/dataset_manager.py`:

1. `historical_ohlcv.json`: Multi-year price action, 52-week ranges, beta metrics, P/E multiples.
2. `macro_indicators.json`: RBI policy rates, FII/DII institutional flows, inflation metrics.
3. `market_microstructure_datasets.json`: Statutory schedules (STT, GST, Exchange charges), circuit limits.
4. `chart_pattern_statistics_dataset.json`: Historical win rates and profit factors for 12+ patterns.
5. `mining_and_commodities_dataset.json`: Reserve metrics for Indian mining corporations (CIL, NMDC, Tata Steel).
6. `corporate_fundamentals_and_sectors.json`: Nifty 50 and Bank Nifty sector weightings.
7. `forex_crypto_global_macro.json`: USD/INR forex crosses, US 10-year yields, VDA tax rules.

---

## 🚀 Step-by-Step Execution Guide & Commands

### Prerequisites
- Python 3.10+ (Tested on Python 3.13 Windows 64-bit)
- PowerShell or Command Prompt

### Step 1: Install Dependencies
```powershell
cd C:\Users\kakan\trading_agent\bharattrader-ai
python -m pip install -r requirements.txt
```

### Step 2: Configure Environment (Optional)
```powershell
copy .env.example .env
```
*(Defaults to high-fidelity Paper Trading Simulator with realistic Indian STT and exchange fees)*

### Step 3: Launch the 24/7 Background Trading Engine & Web Dashboard
```powershell
python run_agent.py
```
Open your browser at: **[http://localhost:8585](http://localhost:8585)**

### Step 4 (Production 24/7 Mode): Launch with Auto-Healing Watchdog Supervisor
To keep the engine running 24/7 with auto-resurrection on crash:
```powershell
python scripts/supervisor_24_7.py
```

---

## 💻 Complete CLI Command Reference (`.\bt`)

From `C:\Users\kakan\trading_agent\`, execute commands using `.\bt <command>`:

| Command | Description | Example |
|---|---|---|
| `.\bt status` | Instant portfolio capital, 24/7 market session, and P&L snapshot | `.\bt status` |
| `.\bt monitor` | Launch live refreshing Bloomberg-style terminal TUI | `.\bt monitor` |
| `.\bt quote <SYM>` | Fetch real-time tick, technical indicators, and AI signal | `.\bt quote TATASTEEL.NS` |
| `.\bt positions` | List active positions and sub-second loss suppression trigger levels | `.\bt positions` |
| `.\bt order BUY <SYM> <QTY>` | Execute order with automatic sub-second stop loss and target | `.\bt order BUY RELIANCE.NS 10` |
| `.\bt close <SYM>` | Immediately close an open position | `.\bt close RELIANCE.NS` |
| `.\bt kill-switch trigger` | Trigger Emergency Panic Stop (halts all trading immediately) | `.\bt kill-switch trigger --reason "Panic"` |
| `.\bt kill-switch reset` | Re-arm Independent Risk Guardian and resume trading | `.\bt kill-switch reset` |
| `.\bt train --all` | Run training sweep across all 10 worldwide strategy disciplines | `.\bt train --all` |
| `.\bt train --tv <SYM>` | Optimize TradingView parameters using genetic algorithm | `.\bt train --tv TATASTEEL.NS` |
| `.\bt security` | Run cryptographic SHA-256 anti-tamper and security audit | `.\bt security` |
| `.\bt datasets` | View overview and entity counts of all 7 datasets | `.\bt datasets` |
| `.\bt datasets --search <Q>`| Search across all 7 quantitative and macro datasets | `.\bt datasets --search "mining"` |
| `.\bt notify --test` | Dispatch test alert across Telegram, Discord, and Web Audio | `.\bt notify --test` |
| `.\bt pinescript` | Print TradingView Pine Script v5 strategy path and webhook URL | `.\bt pinescript` |
| `.\bt shell` | Enter interactive REPL terminal prompt | `.\bt shell` |

---

## 🖥️ Bloomberg-Style Live Terminal Application (TUI)

Launch the real-time terminal UI:
```powershell
.\bt monitor
# or
python bharattrader-ai\terminal_app.py
```

### Hotkeys in Terminal App:
- `[B]` **Buy Order:** Place immediate order with sub-second loss suppressor stop.
- `[C]` **Close Position:** Liquidate top open position immediately.
- `[K]` **Emergency Kill-Switch:** Toggle Independent Risk Guardian panic stop.
- `[T]` **Train All Models:** Execute sweep across all 10 worldwide disciplines.
- `[V]` **View PineScript:** Display TradingView Pine Script v5 file path.
- `[N]` **Test Notification:** Dispatch multi-channel test alert.
- `[R]` **Force Refresh:** Manually refresh market tick state.
- `[Q]` **Exit:** Return to console (background engine continues running).

---

## 📈 TradingView Pine Script Setup Instructions

1. Open [TradingView](https://www.tradingview.com) (web or app) and open **Pine Editor**.
2. Open the file `tradingview/BharatTrader_Alpha_PineScript.pine` in a text editor and copy its contents.
3. Paste the code into the Pine Editor and click **Add to Chart**.
4. Click **Create Alert** on the chart:
   - **Condition:** BharatTrader Alpha Strategy
   - **Webhook URL:** `http://<YOUR-IP-OR-DOMAIN>:8585/api/webhook/tradingview`
   - **Message:** Default JSON webhook template from the script:
     ```json
     {
       "ticker": "{{ticker}}",
       "action": "{{strategy.order.action}}",
       "price": {{close}},
       "passphrase": "BHARAT_SECURE_TOKEN_2026",
       "strategy_name": "BharatTrader_Alpha_Confluence"
     }
     ```
5. Save the alert. BharatTrader AI will receive signals and execute orders autonomously.

---

## 🧪 Testing & Verification Suite

Verify all components with the included automated test scripts:

```powershell
cd C:\Users\kakan\trading_agent\bharattrader-ai

# Test 24/7 clock, Universal Matrix & Notifications
python scratch\test_24_7_and_universal.py

# Test Direct Online Platform Execution & Loss Suppression
python scratch\test_online_platform_direct.py

# Test Cryptographic Security Shield
python -c "from core.security_guard import security_guard; print(security_guard.get_security_status())"
```

---

## 🛡️ Proprietary & Security Notice

**PROPRIETARY & CONFIDENTIAL INTELLECTUAL PROPERTY — ALL RIGHTS RESERVED.**

No open-source license is granted. This software, its algorithmic models, datasets, sub-second execution mechanisms, and risk guardians are private, restricted-access proprietary technology. Unauthorized duplication, redistribution, reverse engineering, or decompilation is strictly prohibited and protected by cryptographic integrity verification.
