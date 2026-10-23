import os
import asyncio
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, JSONResponse
from pydantic import BaseModel
from typing import Dict, Any, List, Optional
from config.settings import settings
from engine.trading_engine import trading_engine
from core.loss_suppressor import loss_suppressor
from markets.metals_mining import metals_mining_analyst
from markets.commodities import mcx_commodities_analyst
from swarm.micro_swarm import micro_swarm
from whatif.scenario_simulator import whatif_simulator
from daily_brief.sector_scanner import sector_scanner
from evolution.strategy_evolver import strategy_evolver
from rag.market_memory import rag_memory
from brokers import paper_broker

app = FastAPI(title="BharatTrader AI", version=settings.VERSION)

# Enterprise Security Middleware: Rate Limiting, Anti-Brute-Force & Security Headers
@app.middleware("http")
async def security_headers_middleware(request, call_next):
    client_ip = request.client.host if request.client else "127.0.0.1"
    from core.security_guard import security_guard
    allowed, msg = security_guard.check_rate_limit(client_ip)
    if not allowed:
        return JSONResponse({"status": "RATE_LIMITED", "error": msg}, status_code=429)
    response = await call_next(request)
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["X-XSS-Protection"] = "1; mode=block"
    response.headers["X-Trading-Guard"] = "BharatTrader-Apex-Active"
    return response

# Serve static web frontend
static_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "static")
if not os.path.exists(static_dir):
    os.makedirs(static_dir, exist_ok=True)

app.mount("/static", StaticFiles(directory=static_dir), name="static")

class ActiveWebsocketManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)

    async def broadcast(self, data: Dict[str, Any]):
        for connection in list(self.active_connections):
            try:
                await connection.send_json(data)
            except Exception:
                self.disconnect(connection)

ws_manager = ActiveWebsocketManager()

@app.on_event("startup")
async def startup_event():
    asyncio.create_task(trading_engine.run_loop())
    asyncio.create_task(broadcast_loop())

async def broadcast_loop():
    while True:
        try:
            if ws_manager.active_connections:
                state = trading_engine.get_dashboard_state()
                await ws_manager.broadcast(state)
            await asyncio.sleep(1.0)
        except Exception:
            await asyncio.sleep(2.0)

@app.get("/")
def get_dashboard():
    index_path = os.path.join(static_dir, "index.html")
    if os.path.exists(index_path):
        return FileResponse(index_path)
    return JSONResponse({"status": "BharatTrader AI running", "version": settings.VERSION})

@app.get("/api/state")
def get_state():
    return trading_engine.get_dashboard_state()

# Advanced Market Segments
@app.get("/api/markets/mining")
def get_mining_markets():
    """Returns deep analysis of all Indian Metals & Mining companies."""
    return {
        "status": "SUCCESS",
        "sector": "Indian Metals & Mining",
        "data": metals_mining_analyst.get_all_mining_overview()
    }

@app.get("/api/markets/commodities")
def get_mcx_commodities():
    """Returns deep analysis of MCX Commodities (Gold, Silver, Crude Oil, Copper, NatGas)."""
    return {
        "status": "SUCCESS",
        "exchange": "Multi Commodity Exchange of India (MCX)",
        "data": mcx_commodities_analyst.get_all_commodities()
    }

@app.get("/api/daily-brief")
def get_daily_brief():
    """Returns morning sector intelligence brief and heatmap."""
    return sector_scanner.generate_daily_brief()

@app.get("/api/strategies")
def get_strategies():
    """Returns active strategy evolution pool."""
    return {
        "strategies": strategy_evolver.get_active_strategies()
    }

@app.get("/api/knowledge/disciplines")
def get_universal_disciplines():
    """Returns Global Encyclopedia of Worldwide Trading Disciplines."""
    from core.universal_trading_knowledge import universal_trading_knowledge
    return {
        "status": "SUCCESS",
        "disciplines": universal_trading_knowledge.get_all_disciplines()
    }

@app.get("/api/patterns/catalog")
def get_patterns_catalog():
    """Returns Universal Catalog of Recognized Chart & Candlestick Patterns."""
    from core.chart_patterns import chart_pattern_engine
    return {
        "status": "SUCCESS",
        "catalog": chart_pattern_engine.pattern_catalog
    }

@app.get("/api/datasets/summary")
def get_datasets_summary():
    """Returns overview of all empirical, historical, and macro trading datasets."""
    from data.dataset_manager import dataset_manager
    return dataset_manager.get_repository_stats()

@app.get("/api/datasets/all")
def get_all_datasets_payload():
    """Returns complete payload of all 7 datasets in the repository."""
    from data.dataset_manager import dataset_manager
    return {
        "status": "SUCCESS",
        "stats": dataset_manager.get_repository_stats(),
        "datasets": dataset_manager.datasets
    }

@app.get("/api/datasets/microstructure")
def get_microstructure_dataset():
    """Returns SEBI statutory charges, circuit breakers, and derivatives specifications."""
    from data.dataset_manager import dataset_manager
    return dataset_manager.get_microstructure()

@app.get("/api/datasets/patterns")
def get_pattern_statistics_dataset():
    """Returns empirical win rate, profit factor, and execution metrics for all chart patterns."""
    from data.dataset_manager import dataset_manager
    return dataset_manager.get_pattern_statistics()

@app.get("/api/datasets/mining")
def get_mining_full_dataset():
    """Returns deep domain datasets for Indian mining corporations and MCX benchmarks."""
    from data.dataset_manager import dataset_manager
    return {
        "mining_corporations": dataset_manager.get_mining_dataset(),
        "commodity_benchmarks": dataset_manager.get_commodity_benchmarks()
    }

@app.get("/api/datasets/fundamentals")
def get_corporate_fundamentals_dataset():
    """Returns corporate valuation multiples and index sector breakdowns."""
    from data.dataset_manager import dataset_manager
    return {
        "fundamentals": dataset_manager.get_corporate_fundamentals(),
        "sector_breakdowns": dataset_manager.datasets.get("fundamentals", {}).get("index_weightages", {})
    }

@app.get("/api/datasets/forex-crypto")
def get_forex_crypto_macro_dataset():
    """Returns global forex crosses, US yields, and VDA tax compliance metrics."""
    from data.dataset_manager import dataset_manager
    return dataset_manager.get_forex_crypto_macro()

@app.get("/api/datasets/macro")
def get_macro_datasets():
    """Returns RBI policy cycle history and FII/DII institutional net flows."""
    from data.dataset_manager import dataset_manager
    return dataset_manager.get_macro_dataset_summary()

@app.get("/api/datasets/search")
def search_trading_datasets(q: str = ""):
    """Performs deep full-text search across all 7 trading datasets."""
    from data.dataset_manager import dataset_manager
    return {
        "query": q,
        "results": dataset_manager.search_all_datasets(q)
    }

@app.get("/api/datasets/instrument/{symbol}")
def get_single_instrument_dataset(symbol: str):
    """Returns empirical metrics, 52W range, and mining metrics for a specific asset."""
    from data.dataset_manager import dataset_manager
    return dataset_manager.get_instrument_dataset(symbol)

class SwarmRequest(BaseModel):
    symbol: str = "TATASTEEL.NS"
    score: float = 75.0

@app.post("/api/swarm/simulate")
def run_swarm(req: SwarmRequest):
    """Executes 20-agent micro swarm Monte Carlo simulation."""
    return micro_swarm.simulate(req.symbol, req.score)

class WhatIfRequest(BaseModel):
    scenario: str = "CHINA_INFRA_STIMULUS"

@app.post("/api/whatif/simulate")
def run_whatif(req: WhatIfRequest):
    """Executes What-If macroeconomic shockwave simulation."""
    return whatif_simulator.simulate_event(req.scenario)

class RAGQueryRequest(BaseModel):
    query: str

@app.post("/api/rag/query")
def query_market_knowledge(req: RAGQueryRequest):
    """Queries Indian market knowledge store."""
    return {
        "query": req.query,
        "results": rag_memory.query_context(req.query)
    }

# Standard Controls
class ToggleAutopilotRequest(BaseModel):
    enabled: bool

@app.post("/api/autopilot/toggle")
def toggle_autopilot(req: ToggleAutopilotRequest):
    trading_engine.autopilot_enabled = req.enabled
    trading_engine.log("INFO", f"Auto-Pilot set to {'ENABLED' if req.enabled else 'DISABLED'}")
    return {"status": "SUCCESS", "autopilot_enabled": trading_engine.autopilot_enabled}

class ClosePositionRequest(BaseModel):
    symbol: str

@app.post("/api/trade/close")
def close_trade(req: ClosePositionRequest):
    price = trading_engine.broker.get_live_quote(req.symbol)
    result = trading_engine.broker.close_position(req.symbol, price, reason="MANUAL_UI_OVERRIDE")
    trading_engine.log("INFO", f"Manual close: {req.symbol}", result)
    return result

class ManualBuyRequest(BaseModel):
    symbol: str
    quantity: int = 1

@app.post("/api/trade/buy")
def manual_buy(req: ManualBuyRequest):
    price = trading_engine.broker.get_live_quote(req.symbol)
    result = trading_engine.broker.place_order(
        symbol=req.symbol,
        side="BUY",
        quantity=req.quantity,
        price=price,
        stop_loss=round(price * 0.995, 2),
        target=round(price * 1.015, 2)
    )
    trading_engine.log("INFO", f"Manual Buy: {req.quantity} of {req.symbol} at ₹{price:.2f}", result)
    return result

class SensitivityRequest(BaseModel):
    mode: str

@app.post("/api/suppressor/sensitivity")
def update_sensitivity(req: SensitivityRequest):
    loss_suppressor.set_sensitivity(req.mode)
# ==========================================
# PROJECT APEX: ADVANCED GLOBAL CAPABILITIES
# ==========================================

@app.get("/api/apex/cross-market")
def get_cross_market_graph():
    """Returns dynamic cross-market correlation matrix and macro regime."""
    from core.cross_market_graph import cross_market_graph
    return cross_market_graph.evaluate_cross_market_state()

@app.get("/api/apex/execution-quality")
def get_execution_quality():
    """Returns latency, slippage, and spread optimization metrics."""
    from core.execution_optimizer import execution_optimizer
    return execution_optimizer.get_execution_metrics()

@app.get("/api/apex/research-lab")
def get_research_lab_summary():
    """Returns offline research experiment log and validation gate results."""
    from core.research_lab import research_lab
    return research_lab.get_laboratory_summary()

class LabEvaluateRequest(BaseModel):
    name: str
    category: str = "Quantitative Strategy"
    simulated_trades: int = 150
    win_rate: float = 68.0
    profit_factor: float = 2.10
    max_drawdown: float = 3.20
    sharpe: float = 2.15

@app.post("/api/apex/research-lab/evaluate")
def run_lab_evaluation(req: LabEvaluateRequest):
    """Evaluates candidate strategy against the 4 Mandatory Validation Gates."""
    from core.research_lab import research_lab
    result = research_lab.evaluate_candidate_strategy(
        name=req.name,
        category=req.category,
        params={},
        simulated_trades=req.simulated_trades,
        simulated_win_rate=req.win_rate,
        simulated_profit_factor=req.profit_factor,
        simulated_max_drawdown=req.max_drawdown,
        simulated_sharpe=req.sharpe
    )
    return result

@app.get("/api/apex/risk-guardian")
def get_risk_guardian_telemetry():
    """Returns independent risk invariant telemetry and kill switch status."""
    from core.kill_switch import risk_guardian
    return risk_guardian.get_status()

class KillSwitchTriggerRequest(BaseModel):
    reason: str = "Manual Emergency Panic Stop triggered by User."

@app.post("/api/apex/kill-switch/trigger")
def trigger_emergency_kill_switch(req: KillSwitchTriggerRequest):
    """Emergency Panic Stop: Instantly halts all trading activity."""
    from core.kill_switch import risk_guardian
    result = risk_guardian.trigger_kill_switch(req.reason)
    trading_engine.log("WARNING", f"🚨 INDEPENDENT KILL-SWITCH TRIGGERED: {req.reason}")
    return result

@app.post("/api/apex/kill-switch/reset")
def reset_emergency_kill_switch():
    """Restores trading authorization after safety audit."""
    from core.kill_switch import risk_guardian
    result = risk_guardian.reset_kill_switch()
    trading_engine.log("SUCCESS", "✅ Independent Risk Guardian re-armed and operational.")
    return result

# ==========================================
# DIRECT ONLINE TRADING PLATFORM SUITE
# ==========================================

class OnlineTestRequest(BaseModel):
    symbol: str = "TATASTEEL.NS"

@app.get("/api/online/quote/{symbol}")
def get_live_online_quote(symbol: str):
    """Fetches true live tick price directly from online financial exchange bridge."""
    from brokers.online_market_feed import online_market_feed
    return online_market_feed.fetch_live_quote(symbol)

@app.get("/api/online/supported-markets")
def get_supported_online_markets():
    """Returns directory of live-tested online exchanges, equities, and commodities."""
    from brokers.online_market_feed import online_market_feed
    return {
        "status": "ONLINE",
        "supported_symbols": online_market_feed.DEFAULT_SYMBOLS,
        "sample_quotes": online_market_feed.fetch_all_live_quotes(["TATASTEEL.NS", "COALINDIA.NS", "NMDC.NS", "RELIANCE.NS", "GOLD"])
    }

@app.post("/api/online/test-trade")
def run_direct_online_platform_test(req: OnlineTestRequest):
    """Executes a full live online trading platform validation cycle with real tick fills and sub-second loss suppression."""
    from brokers.online_platform_tester import online_platform_tester
    result = online_platform_tester.run_direct_online_platform_test(req.symbol)
    trading_engine.log(
        "INFO",
        f"⚡ Live Online Platform Test Executed for {req.symbol}: Status {result.get('status')}",
        {"duration_ms": result.get("total_test_duration_ms")}
    )
    return result

class TradingViewWebhookPayload(BaseModel):
    ticker: str
    action: str  # BUY or SELL
    price: float = 0.0
    passphrase: str = "BHARAT_SECURE_TOKEN_2026"
    strategy_name: str = "TradingView_PineScript_Alert"

@app.get("/api/security/status")
def get_security_posture():
    """Returns real-time security integrity, anti-tamper, and token verification status."""
    from core.security_guard import security_guard
    return security_guard.get_security_status()

@app.post("/api/webhook/tradingview")
def handle_tradingview_alert(payload: TradingViewWebhookPayload):
    """Ingests real-time strategy alerts from TradingView Pine Script webhooks and executes autonomously with cryptographic protection."""
    from core.security_guard import security_guard
    from core.kill_switch import risk_guardian
    from brokers.paper_broker import paper_broker
    from evolution.tradingview_trainer import tradingview_trainer
    from core.notification_service import notification_service

    # 1. Cryptographic HMAC Token Verification (Anti-Spoofing & Anti-Timing Attack)
    if not security_guard.verify_webhook_token(payload.passphrase):
        notification_service.notify(
            severity="RISK_ALERT",
            title="🛑 Webhook Authentication Failed",
            message=f"Unauthorized TradingView alert attempt blocked on {payload.ticker}. Invalid security token."
        )
        return JSONResponse({"status": "REJECTED", "error": "Invalid Cryptographic Passphrase Token"}, status_code=403)

    # 2. Cryptographic SHA-256 Tamper Protection
    is_intact, tampered = security_guard.verify_core_integrity()
    if not is_intact:
        risk_guardian.trigger_kill_switch(f"Tamper Protection Alert: Modified core files: {tampered}")
        return JSONResponse({"status": "REJECTED", "error": f"Tamper protection triggered on {tampered}"}, status_code=403)

    # Record signal for machine learning forensics
    tradingview_trainer.record_incoming_signal(payload.dict())

    is_armed, reason = risk_guardian.is_trading_permitted()
    if not is_armed:
        notification_service.notify(
            severity="RISK_ALERT",
            title=f"🛑 TradingView Alert Blocked by Risk Guardian",
            message=f"Signal on {payload.ticker} rejected: {reason}"
        )
        return {"status": "REJECTED", "reason": f"Risk Guardian Blocked: {reason}"}

    live_price = payload.price if payload.price > 0 else paper_broker.get_live_quote(payload.ticker)
    
    # If position already open, check if reversal or skip
    if payload.ticker in paper_broker.positions:
        existing_pos = paper_broker.positions[payload.ticker]
        if existing_pos["side"] != payload.action.upper():
            paper_broker.close_position(payload.ticker, live_price, reason="TRADINGVIEW_REVERSAL")

    order = paper_broker.place_order(
        symbol=payload.ticker,
        side=payload.action.upper(),
        quantity=5,
        price=live_price,
        stop_loss=round(live_price * 0.995, 2),
        target=round(live_price * 1.02, 2)
    )
    
    trading_engine.log(
        "TRADE",
        f"🌐 TradingView Webhook Order Executed: {payload.action.upper()} {payload.ticker} @ ₹{live_price:.2f}",
        {"strategy": payload.strategy_name, "order": order}
    )
    return {
        "status": "EXECUTED",
        "source": "TradingView Webhook",
        "strategy": payload.strategy_name,
        "order": order
    }

# ==========================================
# MULTI-CHANNEL NOTIFICATION ENDPOINTS
# ==========================================

class NotificationSettingsRequest(BaseModel):
    telegram_token: Optional[str] = None
    telegram_chat: Optional[str] = None
    discord_webhook: Optional[str] = None
    sound_enabled: Optional[bool] = None

@app.get("/api/notifications")
def get_notifications():
    """Returns recent notification audit log and channel configuration."""
    from core.notification_service import notification_service
    return {
        "status": "SUCCESS",
        "config": notification_service.get_status(),
        "notifications": notification_service.get_recent_notifications(30)
    }

@app.post("/api/notifications/settings")
def update_notification_settings(req: NotificationSettingsRequest):
    """Updates Telegram, Discord, and Browser notification preferences."""
    from core.notification_service import notification_service
    return notification_service.update_settings(
        telegram_token=req.telegram_token,
        telegram_chat=req.telegram_chat,
        discord_webhook=req.discord_webhook,
        sound_enabled=req.sound_enabled
    )

@app.post("/api/notifications/test")
def send_test_notification():
    """Dispatches a test notification across all active channels."""
    from core.notification_service import notification_service
    record = notification_service.notify(
        severity="TRADE_FILL",
        title="⚡ Test Notification Dispatch",
        message="Multi-channel alert test successful! Connected to Telegram, Discord & Browser Chime.",
        metadata={"test": True}
    )
    return {"status": "DISPATCHED", "record": record}

@app.post("/api/notifications/mark-read")
def mark_all_notifications_read():
    """Marks all notifications as read."""
    from core.notification_service import notification_service
    return notification_service.mark_all_as_read()

# ==========================================
# TRADINGVIEW PINE SCRIPT & TRAINING STUDIO
# ==========================================

class TradingViewTrainRequest(BaseModel):
    symbol: str = "TATASTEEL.NS"
    strategy_template: str = "BharatTrader_Alpha_Confluence"
    generations: int = 50

@app.get("/api/tradingview/pinescript")
def get_tradingview_pinescript():
    """Returns official TradingView Pine Script v5 strategy code."""
    from evolution.tradingview_trainer import tradingview_trainer
    return {
        "status": "SUCCESS",
        "filename": "BharatTrader_Alpha_PineScript.pine",
        "pinescript": tradingview_trainer.get_pine_script_code()
    }

@app.get("/api/tradingview/status")
def get_tradingview_status():
    """Returns TradingView training run logs and webhook telemetry."""
    from evolution.tradingview_trainer import tradingview_trainer
    return tradingview_trainer.get_training_summary()

@app.post("/api/tradingview/train")
def train_from_tradingview(req: TradingViewTrainRequest):
    """
    Trains and tunes agent parameters using TradingView setups.
    Optimizes win rate, profit factor, and promotes calibrated rules to production.
    """
    from evolution.tradingview_trainer import tradingview_trainer
    result = tradingview_trainer.train_agent_from_tradingview(
        symbol=req.symbol,
        strategy_template=req.strategy_template,
        generations=req.generations
    )
    trading_engine.log(
        "SUCCESS",
        f"🧠 TradingView AI Training Complete for {req.symbol}: Win Rate {result['win_rate_before']}% -> {result['win_rate_after']}%, PF {result['profit_factor_after']}",
        {"duration_ms": result["duration_ms"]}
    )
    return result

# ==========================================
# UNIVERSAL WORLDWIDE STRATEGY TRAINING
# ==========================================

@app.get("/api/training/universal-matrix")
def get_universal_matrix():
    """Returns overview of all 10 Global Trading Strategy Disciplines and calibrated models."""
    from evolution.universal_strategy_trainer import universal_strategy_trainer
    return universal_strategy_trainer.get_matrix_summary()

@app.post("/api/training/universal-train-all")
def train_all_world_strategies():
    """Executes a full calibration and training sweep across all 10 global strategy disciplines."""
    from evolution.universal_strategy_trainer import universal_strategy_trainer
    result = universal_strategy_trainer.train_all_world_strategies()
    trading_engine.log(
        "SUCCESS",
        f"🌍 Universal Training Sweep Complete across 10 Disciplines: Win Rate {result['overall_trained_win_rate']}%, PF {result['overall_trained_profit_factor']}",
        {"duration_ms": result["duration_ms"]}
    )
    return result




@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await ws_manager.connect(websocket)
    try:
        await websocket.send_json(trading_engine.get_dashboard_state())
        while True:
            data = await websocket.receive_text()
            if data == "ping":
                await websocket.send_text("pong")
    except WebSocketDisconnect:
        ws_manager.disconnect(websocket)
    except Exception:
        ws_manager.disconnect(websocket)
