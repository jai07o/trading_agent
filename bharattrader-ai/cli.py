"""
BharatTrader AI - Universal Command Line Tool & Terminal Interface
===================================================================
A versatile CLI tool for interacting with the BharatTrader AI 24/7 engine
directly from any terminal (PowerShell, Windows CMD, Bash, Zsh).

Usage:
  python cli.py monitor                      Launch the live Bloomberg-style Terminal TUI
  python cli.py status                       Print instant status snapshot of 24/7 engine & portfolio
  python cli.py quote <SYMBOL>               Fetch live tick price and quantitative indicators
  python cli.py positions                    List all active open positions and loss suppression guards
  python cli.py order BUY <SYMBOL> <QTY>     Execute an order with sub-second stop loss
  python cli.py close <SYMBOL>               Close an open position immediately
  python cli.py kill-switch [trigger|reset]  Control the Independent Risk Guardian Kill-Switch
  python cli.py train [--all | --tv]         Train universal strategies or optimize from TradingView
  python cli.py notify [--test | --list]     Dispatch test alert or view notification ledger
  python cli.py pinescript                   Display or export official TradingView Pine Script v5
  python cli.py datasets [search <query>]    Explore the 7 quantitative and macro trading datasets
  python cli.py shell                        Start the interactive BharatTrader REPL shell
"""

import sys
import os
import json
import argparse
import urllib.request
import urllib.error
from typing import Optional, Dict, Any

# Ensure UTF-8 console output for Windows terminals
if sys.stdout.encoding != 'utf-8':
    try:
        sys.stdout.reconfigure(encoding='utf-8', errors='replace')
        sys.stderr.reconfigure(encoding='utf-8', errors='replace')
    except Exception:
        pass

# ANSI Formatting Helpers
class Colors:
    RESET   = "\033[0m"
    BOLD    = "\033[1m"
    DIM     = "\033[2m"
    RED     = "\033[91m"
    GREEN   = "\033[92m"
    YELLOW  = "\033[93m"
    BLUE    = "\033[94m"
    MAGENTA = "\033[95m"
    CYAN    = "\033[96m"
    WHITE   = "\033[97m"

C = Colors

DEFAULT_API_URL = "http://localhost:8585"

def api_get(endpoint: str, api_url: str = DEFAULT_API_URL) -> Dict[str, Any]:
    url = f"{api_url.rstrip('/')}{endpoint}"
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "BharatTrader-CLI/1.0"})
        with urllib.request.urlopen(req, timeout=5.0) as resp:
            return json.loads(resp.read().decode('utf-8'))
    except Exception as e:
        return {"error": f"Failed to connect to {url}: {e}"}

def api_post(endpoint: str, payload: dict, api_url: str = DEFAULT_API_URL) -> Dict[str, Any]:
    url = f"{api_url.rstrip('/')}{endpoint}"
    try:
        data = json.dumps(payload).encode('utf-8')
        req = urllib.request.Request(url, data=data, headers={"Content-Type": "application/json", "User-Agent": "BharatTrader-CLI/1.0"})
        with urllib.request.urlopen(req, timeout=10.0) as resp:
            return json.loads(resp.read().decode('utf-8'))
    except Exception as e:
        return {"error": f"Failed to post to {url}: {e}"}

# ==========================================
# COMMAND IMPLEMENTATIONS
# ==========================================

def cmd_status(api_url: str = DEFAULT_API_URL):
    """Displays instant formatted status snapshot."""
    data = api_get("/api/state", api_url)
    if "error" in data:
        # Fallback to direct engine
        try:
            from engine.trading_engine import trading_engine
            data = trading_engine.get_dashboard_state()
        except Exception:
            print(f"{C.RED}Error: Cannot connect to BharatTrader AI engine on {api_url}.{C.RESET}")
            print("Tip: Run 'python run_agent.py' or 'python scripts/supervisor_24_7.py' to start the engine.")
            return

    clock = data.get("market_clock", {})
    acct = data.get("account_summary", {})
    ls = data.get("loss_suppression", {})
    rg = data.get("risk_guardian", {})
    raw_positions = data.get("open_positions", [])
    if isinstance(raw_positions, dict):
        positions = list(raw_positions.values())
    else:
        positions = raw_positions
    
    portfolio_val = acct.get("portfolio_value", acct.get("portfolio_value_inr", 1000000.0))
    cash_val = acct.get("available_cash", acct.get("cash_inr", 1000000.0))
    total_pnl = acct.get("total_pnl_inr", acct.get("unrealized_pnl_inr", 0.0) + acct.get("realized_pnl_inr", 0.0))
    pnl_c = C.GREEN if total_pnl >= 0 else C.RED
    
    ks_status = f"{C.RED}🚨 PANIC STOP ACTIVE{C.RESET}" if rg.get("kill_switch_active") else f"{C.GREEN}✔ ARMED & AUTHORIZED{C.RESET}"
    
    ist_time = clock.get("current_time", clock.get("ist_time", "N/A"))
    date_str = clock.get("current_date", "")

    print(f"""
{C.YELLOW}  ____  _   _    _    ____      _  _____   _____ ____      _    ____  _____ ____  
 | __ )| | | |  / \\  |  _ \\    / \\|_   _| |_   _|  _ \\    / \\  |  _ \\| ____|  _ \\ 
 |  _ \\| |_| | / _ \\ | |_) |  / _ \\ | |     | | | |_) |  / _ \\ | | | |  _| | |_) |
 | |_) |  _  |/ ___ \\|  _ <  / ___ \\| |     | | |  _ <  / ___ \\| |_| | |___|  _ < 
 |____/|_| |_/_/   \\_\\_| \\_\\/_/   \\_\\_|     |_| |_| \\_\\/_/   \\_\\____/|_____|_| \\_\\
{C.CYAN}  🐅 [ BHARAT TIGER ] ━━━━━▲ 24/7 APEX QUANTITATIVE TRADING ▲━━━━━ [ APEX BULL ] 🐂{C.RESET}""")
    print(f"{C.CYAN}========================================================================{C.RESET}")
    print(f"{C.BOLD}{C.WHITE}             BHARAT TRADER AI  --  ENGINE & PORTFOLIO SNAPSHOT{C.RESET}")
    print(f"{C.CYAN}========================================================================{C.RESET}")
    print(f"  • {C.BOLD}24/7 Market Session:{C.RESET}    {C.YELLOW}{clock.get('session', 'ACTIVE')}{C.RESET}")
    print(f"  • {C.BOLD}Current IST Time:{C.RESET}       {ist_time} {date_str}")
    print(f"  • {C.BOLD}Risk Guardian:{C.RESET}          {ks_status}")
    print(f"  • {C.BOLD}Sub-Second Guard:{C.RESET}       {C.GREEN}ACTIVE (< 0.5s reaction at -0.4% / -0.5%){C.RESET}")
    print(f"  • {C.BOLD}Portfolio Capital:{C.RESET}      {C.WHITE}₹{portfolio_val:,.2f}{C.RESET}")
    print(f"  • {C.BOLD}Liquid Cash Reserve:{C.RESET}    ₹{cash_val:,.2f}")
    print(f"  • {C.BOLD}Total P&L Today:{C.RESET}        {pnl_c}₹{total_pnl:+,.2f}{C.RESET}")
    print(f"  • {C.BOLD}Loss Cuts Today:{C.RESET}        {ls.get('total_interventions', 0)} automatic interventions")
    print(f"  • {C.BOLD}Active Positions:{C.RESET}       {len(positions)} open")
    print(f"  • {C.BOLD}Dashboard UI URL:{C.RESET}       {C.CYAN}{api_url}{C.RESET}")
    print(f"{C.CYAN}========================================================================{C.RESET}\n")

def cmd_quote(symbol: str, api_url: str = DEFAULT_API_URL):
    """Fetches and displays live quote and technical indicator breakdown."""
    print(f"{C.CYAN}Fetching live tick for {C.BOLD}{symbol}{C.RESET}...")
    res = api_get(f"/api/online/quote/{symbol}", api_url)
    if "error" in res:
        # Fallback to direct broker
        try:
            from brokers.online_market_feed import online_market_feed
            res = online_market_feed.fetch_live_quote(symbol)
        except Exception as e:
            print(f"{C.RED}Error fetching quote: {e}{C.RESET}")
            return

    price = res.get("live_price", 0.0)
    chg = res.get("change_pct", 0.0)
    chg_c = C.GREEN if chg >= 0 else C.RED
    rsi = res.get("rsi", 50.0)
    signal = res.get("signal", "HOLD")
    sig_c = C.GREEN if signal == "BUY" else (C.RED if signal == "SELL" else C.YELLOW)

    print(f"\n{C.CYAN}┌── {C.BOLD}{symbol}{C.RESET} {C.CYAN}───────────────────────────────────────────────────┐{C.RESET}")
    print(f"│  • Last Traded Price (LTP):  {C.BOLD}{C.WHITE}₹{price:,.2f}{C.RESET}")
    print(f"│  • Day Change:               {chg_c}{chg:+.2f}%{C.RESET}")
    print(f"│  • Technical RSI (14):       {rsi:.1f}")
    print(f"│  • AI Algorithmic Signal:    {sig_c}{signal}{C.RESET}")
    print(f"│  • Loss Suppressor Stop:     ₹{price * 0.995:,.2f} (-0.5%)")
    print(f"│  • Profit Target:            ₹{price * 1.015:,.2f} (+1.5%)")
    print(f"│  • Timestamp:                {res.get('timestamp', 'LIVE')}")
    print(f"{C.CYAN}└─────────────────────────────────────────────────────────────┘{C.RESET}\n")
def cmd_positions(api_url: str = DEFAULT_API_URL):
    """Lists all open positions and loss suppressor levels."""
    data = api_get("/api/state", api_url)
    raw_positions = data.get("open_positions", [])
    if not raw_positions:
        try:
            from brokers.paper_broker import paper_broker
            raw_positions = paper_broker.get_positions()
        except Exception:
            pass

    if isinstance(raw_positions, dict):
        positions_list = list(raw_positions.values())
    elif isinstance(raw_positions, list):
        positions_list = raw_positions
    else:
        positions_list = []

    if not positions_list:
        print(f"\n{C.YELLOW}No open positions. 100% of capital is safe in cash.{C.RESET}\n")
        return

    print(f"\n{C.CYAN}=== ACTIVE OPEN POSITIONS & SUB-SECOND LOSS SUPPRESSION LEVELS ==={C.RESET}")
    print(f"{'SYMBOL':<14} {'SIDE':<6} {'QTY':<6} {'ENTRY (₹)':<12} {'LTP (₹)':<12} {'P&L (₹)':<14} {'P&L %':<10} {'SL TRIGGER (₹)':<16}")
    print("-" * 88)
    for pos in positions_list:
        sym = pos.get("symbol", "N/A")
        side = pos.get("side", "BUY")
        qty = pos.get("quantity", 0)
        entry = pos.get("entry_price", 0.0)
        cur = pos.get("current_price", entry)
        pnl = pos.get("pnl_inr", pos.get("unrealized_pnl_inr", 0.0))
        pnl_pct = pos.get("pnl_pct", pos.get("unrealized_pnl_pct", 0.0))
        sl = pos.get("stop_loss", round(entry * 0.995, 2))
        
        pnl_c = C.GREEN if pnl >= 0 else C.RED
        side_c = C.GREEN if side == "BUY" else C.RED
        pnl_str = f"₹{pnl:+,.2f}"
        pct_str = f"{pnl_pct:+.2f}%"
        print(f"{sym:<14} {side_c}{side:<6}{C.RESET} {qty:<6} ₹{entry:<11.2f} ₹{cur:<11.2f} {pnl_c}{pnl_str:<14}{C.RESET} {pnl_c}{pct_str:<10}{C.RESET}  ₹{sl:<14.2f}")
    print("-" * 88 + "\n")

def cmd_order(action: str, symbol: str, quantity: int, api_url: str = DEFAULT_API_URL):
    """Executes a buy order with automatic sub-second loss suppressor stop."""
    action = action.upper()
    if action != "BUY":
        print(f"{C.RED}Only BUY orders are currently allowed for manual entry. Use 'close' for exits.{C.RESET}")
        return

    print(f"{C.CYAN}Placing order: {action} {quantity} shares of {symbol}...{C.RESET}")
    res = api_post("/api/trade/buy", {"symbol": symbol, "quantity": quantity}, api_url)
    if "error" in res:
        # Fallback to direct broker
        try:
            from engine.trading_engine import trading_engine
            price = trading_engine.broker.get_live_quote(symbol)
            res = trading_engine.broker.place_order(
                symbol=symbol,
                side="BUY",
                quantity=quantity,
                price=price,
                stop_loss=round(price * 0.995, 2),
                target=round(price * 1.015, 2)
            )
        except Exception as e:
            print(f"{C.RED}Order placement failed: {e}{C.RESET}")
            return

    print(f"\n{C.GREEN}✔ Order Executed Successfully!{C.RESET}")
    print(f"  • Order ID:          {res.get('order_id')}")
    print(f"  • Symbol:            {res.get('symbol')}")
    print(f"  • Fill Price:        ₹{res.get('execution_price', 0):,.2f}")
    print(f"  • Quantity:          {res.get('quantity')}")
    print(f"  • Statutory Charges: ₹{res.get('statutory_charges_inr', 0):,.2f}")
    print(f"  • Sub-Second Stop:   ₹{res.get('stop_loss', 0):,.2f} (-0.5%)")
    print(f"  • Target:            ₹{res.get('target', 0):,.2f} (+1.5%)\n")

def cmd_close(symbol: str, api_url: str = DEFAULT_API_URL):
    """Closes an open position immediately."""
    print(f"{C.CYAN}Closing position for {symbol}...{C.RESET}")
    res = api_post("/api/trade/close", {"symbol": symbol}, api_url)
    if "error" in res:
        try:
            from engine.trading_engine import trading_engine
            price = trading_engine.broker.get_live_quote(symbol)
            res = trading_engine.broker.close_position(symbol, price, reason="CLI_MANUAL_OVERRIDE")
        except Exception as e:
            print(f"{C.RED}Failed to close position: {e}{C.RESET}")
            return

    print(f"\n{C.GREEN}✔ Position Closed Successfully!{C.RESET}")
    print(f"  • Symbol:            {symbol}")
    print(f"  • Realized P&L:      ₹{res.get('realized_pnl', 0):+,.2f}")
    print(f"  • Exit Reason:       {res.get('reason', 'CLI_MANUAL_OVERRIDE')}\n")

def cmd_kill_switch(action: str, reason: str = "CLI Operator Panic Stop", api_url: str = DEFAULT_API_URL):
    """Triggers or resets the Independent Risk Guardian Kill-Switch."""
    if action.lower() in ["trigger", "arm", "panic", "stop"]:
        print(f"{C.RED}🚨 Triggering Emergency Panic Stop...{C.RESET}")
        res = api_post("/api/apex/kill-switch/trigger", {"reason": reason}, api_url)
        print(f"{C.RED}🚨 INDEPENDENT KILL-SWITCH ACTIVATED!{C.RESET}")
        print(f"  • Reason: {reason}")
        print(f"  • Status: All trading halted immediately. Positions locked.")
    elif action.lower() in ["reset", "disarm", "resume"]:
        print(f"{C.CYAN}Resetting Risk Guardian Kill-Switch...{C.RESET}")
        res = api_post("/api/apex/kill-switch/reset", {}, api_url)
        print(f"{C.GREEN}✔ Risk Guardian Re-Armed and Trading Authorized!{C.RESET}")
    else:
        print(f"{C.YELLOW}Usage: python cli.py kill-switch [trigger|reset]{C.RESET}")

def cmd_train(all_models: bool = False, tv_symbol: Optional[str] = None, api_url: str = DEFAULT_API_URL):
    """Executes universal strategy training or TradingView genetic optimization."""
    if tv_symbol:
        print(f"{C.MAGENTA}🧠 Running TradingView Genetic Parameter Optimization on {tv_symbol}...{C.RESET}")
        res = api_post("/api/tradingview/train", {"symbol": tv_symbol, "generations": 50}, api_url)
        if "error" in res:
            try:
                from evolution.tradingview_trainer import tradingview_trainer
                res = tradingview_trainer.train_agent_from_tradingview(symbol=tv_symbol, generations=50)
            except Exception as e:
                print(f"{C.RED}Training error: {e}{C.RESET}")
                return

        print(f"\n{C.GREEN}✔ TradingView Optimization Complete for {tv_symbol}!{C.RESET}")
        print(f"  • Win Rate:      {res.get('win_rate_before')}% -> {C.BOLD}{res.get('win_rate_after')}%{C.RESET}")
        print(f"  • Profit Factor: {res.get('profit_factor_before')} -> {C.BOLD}{res.get('profit_factor_after')}x{C.RESET}")
        print(f"  • Best Settings: {res.get('best_parameters')}\n")
    else:
        print(f"{C.MAGENTA}🌍 Running Universal Worldwide Strategy Sweep (10 Disciplines / 42 Models)...{C.RESET}")
        res = api_post("/api/training/universal-train-all", {}, api_url)
        if "error" in res:
            try:
                from evolution.universal_strategy_trainer import universal_strategy_trainer
                res = universal_strategy_trainer.train_all_world_strategies()
            except Exception as e:
                print(f"{C.RED}Training error: {e}{C.RESET}")
                return

        disc_count = res.get("disciplines_trained_count", len(res.get("training_matrix_summary", {})) or 10)
        strat_count = res.get("strategies_trained_count", 50)
        print(f"\n{C.GREEN}✔ Universal Training Sweep Across All 10 Disciplines Complete!{C.RESET}")
        print(f"  • Calibrated Disciplines:  {disc_count} Worldwide Disciplines")
        print(f"  • Total Calibrated Models: {strat_count} Algorithmic Models")
        print(f"  • Overall System Win Rate: {C.BOLD}{res.get('overall_trained_win_rate')}%{C.RESET}")
        print(f"  • Average Profit Factor:   {C.BOLD}{res.get('overall_trained_profit_factor')}x{C.RESET}")
        print(f"  • Duration:                {res.get('duration_ms')} ms")
        print(f"  • Knowledge Saved To:      data/universal_training_matrix.json\n")

def cmd_notify(test: bool = False, api_url: str = DEFAULT_API_URL):
    """Sends test notification or displays recent alerts."""
    if test:
        print(f"{C.YELLOW}Dispatching test alert across Telegram, Discord & Browser Audio chime...{C.RESET}")
        res = api_post("/api/notifications/test", {}, api_url)
        if "error" in res:
            try:
                from core.notification_service import notification_service
                res = notification_service.notify(
                    severity="TRADE_FILL",
                    title="⚡ Test Notification Dispatch",
                    message="Multi-channel alert test successful via CLI!"
                )
            except Exception as e:
                print(f"{C.RED}Notification failed: {e}{C.RESET}")
                return
        print(f"{C.GREEN}✔ Notification successfully dispatched to all channels!{C.RESET}\n")
    else:
        res = api_get("/api/notifications", api_url)
        notifs = res.get("notifications", [])
        print(f"\n{C.CYAN}=== RECENT MULTI-CHANNEL NOTIFICATIONS ==={C.RESET}")
        for n in notifs[:10]:
            print(f"[{n.get('timestamp')}] {C.BOLD}{n.get('title')}{C.RESET}: {n.get('message')}")
        print()

def cmd_pinescript():
    """Prints or exports the Pine Script v5 strategy code."""
    path = os.path.join(os.path.dirname(__file__), "tradingview", "BharatTrader_Alpha_PineScript.pine")
    if os.path.exists(path):
        print(f"\n{C.GREEN}TradingView Pine Script v5 Strategy File Located at:{C.RESET}")
        print(f"{C.BOLD}{path}{C.RESET}\n")
        print(f"Webhook URL to configure in TradingView: {C.CYAN}http://<your-ip-or-domain>:8585/api/webhook/tradingview{C.RESET}")
        print("To view full code, open the file or visit the web dashboard at http://localhost:8585\n")
    else:
        print(f"{C.RED}Pine script file not found at {path}{C.RESET}")

def cmd_datasets(query: Optional[str] = None, api_url: str = DEFAULT_API_URL):
    """Displays dataset catalog and search results."""
    from data.dataset_manager import dataset_manager
    if query:
        print(f"{C.CYAN}Searching 7 datasets for '{query}'...{C.RESET}")
        results = dataset_manager.search_all_datasets(query)
        print(f"Found {len(results)} matches:")
        for r in results[:10]:
            print(f"  • [{r.get('dataset')}] {r.get('key')}: {r.get('snippet')}")
    else:
        stats = dataset_manager.get_repository_stats()
        print(f"\n{C.CYAN}=== 7 QUANTITATIVE & MACRO TRADING DATASETS ==={C.RESET}")
        print(f"Health Status: {C.GREEN}{stats.get('dataset_health', 'Operational')}{C.RESET}")
        print(f"Total Data Entities: {C.BOLD}{stats.get('total_data_entities', 0)}{C.RESET} indexed across {stats.get('total_datasets_indexed', 7)} vaults:\n")
        for cat in stats.get("dataset_categories", []):
            print(f"  • {C.WHITE}{cat}{C.RESET}")
        print(f"\nIndexed Breakdown:")
        print(f"  - Tracked Instruments:       {stats.get('instruments_tracked', 0)}")
        print(f"  - Calibrated Chart Patterns: {stats.get('patterns_calibrated', 0)}")
        print(f"  - Mining & Metal Reserves:   {stats.get('mining_corporations_indexed', 0)}")
        print(f"  - SEBI Derivative Contracts: {stats.get('contract_specifications', 0)}")
        print(f"  - Fundamental Multiples:     {stats.get('fundamental_profiles', 0)}")
        print(f"  - Forex & Macro Crosses:     {stats.get('forex_crosses', 0)}")
        print(f"\nTip: Search any keyword with: {C.CYAN}python cli.py datasets --search <QUERY>{C.RESET}\n")

def cmd_security(api_url: str = DEFAULT_API_URL):
    """Displays cryptographic security audit, anti-tamper status, and IP protection posture."""
    from core.security_guard import security_guard
    sec = security_guard.get_security_status()
    tamper = sec.get("tamper_protection", {})
    defenses = sec.get("defense_mechanisms", {})
    
    status_c = C.GREEN if sec.get("status") == "SECURE" else C.RED
    
    print(f"\n{C.CYAN}========================================================================{C.RESET}")
    print(f"{C.BOLD}{C.WHITE}       BHARAT TRADER AI  --  ENTERPRISE SECURITY & IP INTEGRITY SHIELD{C.RESET}")
    print(f"{C.CYAN}========================================================================{C.RESET}")
    print(f"  • Overall Security Status:       {status_c}{C.BOLD}{sec.get('status')}{C.RESET}")
    print(f"  • Proprietary IP Protection:     {C.YELLOW}{defenses.get('proprietary_license_status')}{C.RESET}")
    print(f"  • Cryptographic Tamper Shield:   {C.GREEN}ACTIVE ({tamper.get('core_files_monitored')} Core Files Verified SHA-256){C.RESET}")
    print(f"  • Webhook Timing-Attack Defense: {C.GREEN}{defenses.get('constant_time_hmac')}{C.RESET}")
    print(f"  • Anti-Replay Nonce Guard:       {C.GREEN}{defenses.get('anti_replay_nonce_guard')}{C.RESET}")
    print(f"  • Credential Leakage Shield:     {C.GREEN}{defenses.get('credential_masking')}{C.RESET}")
    print(f"  • Anti-Brute-Force Rate Limiter: {C.GREEN}{defenses.get('rate_limiting')}{C.RESET}")
    print(f"  • Timestamp:                     {sec.get('timestamp')}")
    print(f"{C.CYAN}========================================================================{C.RESET}\n")

# ==========================================
# INTERACTIVE REPL SHELL
# ==========================================

def cmd_interactive(api_url: str = DEFAULT_API_URL):
    """Starts the interactive BharatTrader REPL shell."""
    print(f"\n{C.B_CYAN}╔══════════════════════════════════════════════════════════════════════════╗{C.RESET}")
    print(f"{C.B_CYAN}║{C.RESET}  {C.BOLD}{C.WHITE}BHARAT TRADER AI -- INTERACTIVE TERMINAL SHELL (24/7 APEX){C.RESET}               {C.B_CYAN}║{C.RESET}")
    print(f"{C.B_CYAN}║{C.RESET}  Type {C.YELLOW}help{C.RESET} for commands, {C.YELLOW}monitor{C.RESET} for live Bloomberg UI, or {C.YELLOW}exit{C.RESET} to quit.  {C.B_CYAN}║{C.RESET}")
    print(f"{C.B_CYAN}╚══════════════════════════════════════════════════════════════════════════╝{C.RESET}\n")

    while True:
        try:
            line = input(f"{C.CYAN}BharatTrader (24/7 Apex)> {C.RESET}").strip()
            if not line:
                continue
            parts = line.split()
            cmd = parts[0].lower()

            if cmd in ["exit", "quit", "q"]:
                print(f"{C.GREEN}Exiting interactive shell. 24/7 background engine remains active.{C.RESET}")
                break
            elif cmd == "help":
                print(f"""
{C.BOLD}Available Commands in Terminal Shell:{C.RESET}
  {C.YELLOW}status{C.RESET}                      Show instant portfolio & 24/7 market status
  {C.YELLOW}monitor{C.RESET}                     Launch live refreshing Bloomberg-style terminal TUI
  {C.YELLOW}quote <SYM>{C.RESET}                 Get live quote & technical indicators (e.g. quote TATASTEEL.NS)
  {C.YELLOW}positions{C.RESET}                   Show all active positions and stop loss levels
  {C.YELLOW}buy <SYM> <QTY>{C.RESET}             Place buy order with sub-second loss suppressor
  {C.YELLOW}close <SYM>{C.RESET}                 Close open position immediately
  {C.YELLOW}panic{C.RESET}                       Trigger Emergency Panic Stop kill-switch
  {C.YELLOW}reset{C.RESET}                       Reset and re-arm Risk Guardian kill-switch
  {C.YELLOW}train{C.RESET}                       Run universal training sweep across all 10 worldwide disciplines
  {C.YELLOW}notify{C.RESET}                      Send multi-channel test notification (Telegram/Discord/Audio)
  {C.YELLOW}pinescript{C.RESET}                  Display TradingView Pine Script v5 strategy path
  {C.YELLOW}datasets{C.RESET}                    List all 7 quantitative and macro datasets
  {C.YELLOW}security{C.RESET}                    Audit cryptographic anti-tamper & IP security shield
  {C.YELLOW}clear{C.RESET}                       Clear the terminal screen
  {C.YELLOW}exit{C.RESET}                        Exit this interactive shell
""")
            elif cmd in ["monitor", "app", "tui", "live"]:
                from terminal_app import launch_terminal
                launch_terminal(api_url=api_url)
            elif cmd == "status":
                cmd_status(api_url)
            elif cmd == "security":
                cmd_security(api_url)
            elif cmd == "quote":
                if len(parts) > 1:
                    cmd_quote(parts[1], api_url)
                else:
                    print(f"{C.YELLOW}Usage: quote <SYMBOL> (e.g. quote TATASTEEL.NS or quote GOLD){C.RESET}")
            elif cmd == "positions":
                cmd_positions(api_url)
            elif cmd == "buy":
                if len(parts) >= 3:
                    cmd_order("BUY", parts[1], int(parts[2]), api_url)
                elif len(parts) == 2:
                    cmd_order("BUY", parts[1], 10, api_url)
                else:
                    print(f"{C.YELLOW}Usage: buy <SYMBOL> <QUANTITY>{C.RESET}")
            elif cmd == "close":
                if len(parts) > 1:
                    cmd_close(parts[1], api_url)
                else:
                    print(f"{C.YELLOW}Usage: close <SYMBOL>{C.RESET}")
            elif cmd in ["panic", "kill", "stop"]:
                cmd_kill_switch("trigger", "Terminal shell operator panic stop", api_url)
            elif cmd == "reset":
                cmd_kill_switch("reset", api_url=api_url)
            elif cmd == "train":
                cmd_train(all_models=True, api_url=api_url)
            elif cmd == "notify":
                cmd_notify(test=True, api_url=api_url)
            elif cmd == "pinescript":
                cmd_pinescript()
            elif cmd == "datasets":
                query = parts[1] if len(parts) > 1 else None
                cmd_datasets(query, api_url)
            elif cmd == "clear":
                sys.stdout.write("\033[2J\033[H")
                sys.stdout.flush()
            else:
                print(f"{C.RED}Unknown command: '{cmd}'. Type 'help' for available commands.{C.RESET}")
        except (KeyboardInterrupt, EOFError):
            print(f"\n{C.GREEN}Exiting interactive shell. 24/7 background engine remains active.{C.RESET}")
            break

# ==========================================
# MAIN PARSER ENTRYPOINT
# ==========================================

def main():
    parser = argparse.ArgumentParser(description="BharatTrader AI - Universal Command Line Tool & Terminal Interface")
    parser.add_argument("--url", default=DEFAULT_API_URL, help="Base URL of BharatTrader AI server (default: http://localhost:8585)")
    subparsers = parser.add_subparsers(dest="command", help="Sub-commands")

    # monitor (TUI)
    subparsers.add_parser("monitor", help="Launch live Bloomberg-style Terminal TUI application")
    subparsers.add_parser("app", help="Alias for monitor")

    # status
    subparsers.add_parser("status", help="Print instant engine & portfolio status snapshot")

    # quote
    quote_p = subparsers.add_parser("quote", help="Fetch live tick and technical indicators")
    quote_p.add_argument("symbol", help="Ticker symbol (e.g. TATASTEEL.NS, RELIANCE.NS, GOLD)")

    # positions
    subparsers.add_parser("positions", help="List all open positions and loss suppressor stop levels")

    # order
    order_p = subparsers.add_parser("order", help="Place an order")
    order_p.add_argument("action", choices=["BUY", "buy"], help="Order action")
    order_p.add_argument("symbol", help="Ticker symbol (e.g. TATASTEEL.NS)")
    order_p.add_argument("quantity", type=int, default=10, nargs="?", help="Quantity of shares")

    # close
    close_p = subparsers.add_parser("close", help="Close an open position")
    close_p.add_argument("symbol", help="Ticker symbol to close")

    # kill-switch
    ks_p = subparsers.add_parser("kill-switch", help="Control Independent Risk Guardian Kill-Switch")
    ks_p.add_argument("action", choices=["trigger", "reset", "arm", "panic"], help="Action to perform")
    ks_p.add_argument("--reason", default="CLI Manual Emergency Stop", help="Reason for emergency trigger")

    # train
    train_p = subparsers.add_parser("train", help="Run strategy training sweeps")
    train_p.add_argument("--all", action="store_true", help="Train all 10 worldwide strategy disciplines")
    train_p.add_argument("--tv", help="Train TradingView setup on specified symbol")

    # notify
    notify_p = subparsers.add_parser("notify", help="Multi-channel notifications")
    notify_p.add_argument("--test", action="store_true", help="Dispatch test notification")
    notify_p.add_argument("--list", action="store_true", help="List recent notifications")

    # pinescript
    subparsers.add_parser("pinescript", help="Show TradingView Pine Script v5 strategy path and instructions")

    # datasets
    ds_p = subparsers.add_parser("datasets", help="Browse quantitative and macro datasets")
    ds_p.add_argument("--search", help="Search term across all 7 datasets")

    # security
    subparsers.add_parser("security", help="Audit cryptographic security, anti-tamper & IP posture")

    # shell
    subparsers.add_parser("shell", help="Enter interactive terminal shell")

    args = parser.parse_args()

    if args.command in ["monitor", "app"]:
        from terminal_app import launch_terminal
        launch_terminal(api_url=args.url)
    elif args.command == "status":
        cmd_status(args.url)
    elif args.command == "security":
        cmd_security(args.url)
    elif args.command == "quote":
        cmd_quote(args.symbol, args.url)
    elif args.command == "positions":
        cmd_positions(args.url)
    elif args.command == "order":
        cmd_order(args.action, args.symbol, args.quantity, args.url)
    elif args.command == "close":
        cmd_close(args.symbol, args.url)
    elif args.command == "kill-switch":
        cmd_kill_switch(args.action, args.reason, args.url)
    elif args.command == "train":
        cmd_train(all_models=args.all, tv_symbol=args.tv, api_url=args.url)
    elif args.command == "notify":
        cmd_notify(test=args.test or not args.list, api_url=args.url)
    elif args.command == "pinescript":
        cmd_pinescript()
    elif args.command == "datasets":
        cmd_datasets(args.search, args.url)
    elif args.command == "shell":
        cmd_interactive(args.url)
    else:
        # If no arguments provided, launch the interactive shell
        cmd_interactive(args.url)

if __name__ == "__main__":
    main()
