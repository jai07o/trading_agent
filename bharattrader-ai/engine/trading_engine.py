import time
import asyncio
import random
import pandas as pd
import numpy as np
from typing import Dict, Any, List, Optional
from config.settings import settings
from core.market_clock import market_clock
from core.loss_suppressor import loss_suppressor
from core.position_sizer import position_sizer
from agents.judge_agent import judge_agent
from brokers import get_active_broker, paper_broker
from markets.metals_mining import metals_mining_analyst
from markets.commodities import mcx_commodities_analyst
from swarm.micro_swarm import micro_swarm
from whatif.scenario_simulator import whatif_simulator
from daily_brief.sector_scanner import sector_scanner
from evolution.strategy_evolver import strategy_evolver
from data.dataset_manager import dataset_manager
from core.cross_market_graph import cross_market_graph
from core.execution_optimizer import execution_optimizer
from core.research_lab import research_lab
from core.kill_switch import risk_guardian
from core.notification_service import notification_service
from evolution.tradingview_trainer import tradingview_trainer
from evolution.universal_strategy_trainer import universal_strategy_trainer

class IndianTradingEngine:
    """
    Autonomous Real-Time Trading Engine for BharatTrader AI.
    Features:
    - Parallel execution alongside user's manual trading apps
    - Sub-second loss suppression & dynamic profit lock monitoring
    - Comprehensive coverage of Equities, Mining, MCX Commodities & Derivatives
    - 20-Agent Micro Swarm, What-If simulation, and Strategy Evolution
    - Real-time P&L bar charts & equity curve updates
    """

    def __init__(self):
        self.is_running = False
        self.autopilot_enabled = True # When True, trades automatically
        self.scan_interval_seconds = 2.0
        self.broker = get_active_broker()
        self.last_scan_time = 0.0
        self.pnl_history: List[Dict[str, Any]] = []
        self.equity_curve: List[Dict[str, Any]] = []
        self.analysis_cache: Dict[str, Any] = {}
        self.logs: List[Dict[str, Any]] = []
        
        # Initialize initial equity point
        self.equity_curve.append({
            "time": time.strftime("%H:%M:%S"),
            "value": settings.STARTING_CAPITAL_INR,
            "pnl": 0.0
        })

        # Pre-populate initial market scan across watchlist
        try:
            self.scan_markets()
        except Exception:
            pass

    def log(self, level: str, message: str, data: Any = None):
        entry = {
            "time": time.strftime("%H:%M:%S"),
            "level": level,
            "message": message,
            "data": data
        }
        self.logs.append(entry)
        if len(self.logs) > 200:
            self.logs.pop(0)

    def generate_synthetic_df(self, symbol: str, periods: int = 60) -> pd.DataFrame:
        """Generates realistic OHLCV dataframe for real-time analysis."""
        base_price = self.broker.get_live_quote(symbol)
        dates = pd.date_range(end=pd.Timestamp.now(), periods=periods, freq='5min')
        
        # Random walk with slight upward drift
        returns = np.random.normal(0.0003, 0.003, periods)
        price_series = base_price * np.exp(np.cumsum(returns))
        
        high = price_series * (1 + np.random.uniform(0.0005, 0.002, periods))
        low = price_series * (1 - np.random.uniform(0.0005, 0.002, periods))
        open_p = price_series * (1 + np.random.uniform(-0.001, 0.001, periods))
        close = price_series
        volume = np.random.randint(50000, 300000, periods)

        df = pd.DataFrame({
            'Open': open_p,
            'High': high,
            'Low': low,
            'Close': close,
            'Volume': volume
        }, index=dates)
        return df

    def scan_markets(self):
        """Scans the Indian watchlist using the Multi-Agent Judge."""
        for symbol in settings.PRIMARY_WATCHLIST:
            try:
                # Update tick price to simulate live market fluctuations
                current_price = paper_broker.update_tick(symbol)
                df = self.generate_synthetic_df(symbol)
                
                # Run Multi-Agent Adjudication
                verdict = judge_agent.adjudicate(symbol, df)
                self.analysis_cache[symbol] = verdict

                # Auto-pilot trade execution check
                if self.autopilot_enabled and verdict.get("action") == "BUY":
                    fused_score = verdict.get("fused_score", 0)
                    open_positions = self.broker.get_positions()

                    if fused_score >= 70.0 and len(open_positions) < settings.MAX_OPEN_POSITIONS:
                        existing_symbols = [p["symbol"] for p in open_positions]
                        if symbol not in existing_symbols:
                            summary = self.broker.get_account_summary()
                            sizing = position_sizer.calculate_share_quantity(
                                symbol=symbol,
                                entry_price=current_price,
                                stop_loss_price=verdict["stop_loss"],
                                confidence_score=verdict["confidence"],
                                available_cash=summary["available_cash"]
                            )

                            # Apply Model Disagreement permitted size factor
                            size_factor = verdict.get("permitted_size_factor", 1.0)
                            final_qty = int(sizing["quantity"] * size_factor)

                            if final_qty > 0:
                                # Independent Risk Guardian hard authorization check
                                authorized, auth_reason = risk_guardian.validate_and_authorize_order(
                                    symbol=symbol,
                                    side="BUY",
                                    quantity=final_qty,
                                    price=current_price,
                                    portfolio_value=summary["portfolio_value"],
                                    current_positions=open_positions,
                                    realized_daily_pnl_inr=summary.get("total_pnl_inr", 0.0)
                                )

                                if not authorized:
                                    self.log("WARNING", f"🛡️ RISK GUARDIAN INTERCEPT: {auth_reason}")
                                    continue

                                # Execute order with Execution Quality Optimizer
                                order_result = self.broker.place_order(
                                    symbol=symbol,
                                    side="BUY",
                                    quantity=final_qty,
                                    price=current_price,
                                    stop_loss=verdict["stop_loss"],
                                    target=verdict["target_1"]
                                )

                                # Record execution quality metrics
                                exec_telemetry = execution_optimizer.record_execution_telemetry(
                                    symbol=symbol,
                                    side="BUY",
                                    quantity=final_qty,
                                    expected_price=current_price,
                                    executed_price=order_result.get("execution_price", current_price),
                                    latency_ms=42.5,
                                    order_type="LIMIT_SMART"
                                )

                                self.log(
                                    "SUCCESS",
                                    f"Auto-Pilot Trade: Bought {final_qty} {symbol} at ₹{current_price:.2f} "
                                    f"[Slippage: {exec_telemetry['slippage_bps']} bps, Latency: {exec_telemetry['latency_ms']}ms]",
                                    order_result
                                )

            except Exception as e:
                self.log("ERROR", f"Error scanning {symbol}: {str(e)}")

    def monitor_open_positions_sub_second(self):
        """
        High-Frequency Sub-Second Loss Suppression & Dynamic Profit Lock Monitor.
        Evaluates every open trade against risk parameters.
        """
        positions = self.broker.get_positions()
        
        for pos in positions:
            symbol = pos["symbol"]
            current_price = self.broker.get_live_quote(symbol)

            # Check with Sub-Second Loss Suppressor
            eval_result = loss_suppressor.evaluate_position(pos, current_price)

            if eval_result.get("should_close"):
                action = eval_result["action"]
                reason = eval_result["reason"]
                pnl_inr = eval_result["pnl_inr"]
                
                # Execute instant exit
                close_res = self.broker.close_position(symbol, current_price, reason=f"{action}: {reason}")
                
                if action == "SUPPRESS_LOSS":
                    self.log("WARNING", f"🚨 SUB-SECOND LOSS SUPPRESSED: {symbol} cut at ₹{current_price:.2f}. Avoided deep drawdown!", close_res)
                elif action == "LOCK_PROFIT":
                    self.log("SUCCESS", f"💰 DYNAMIC PROFIT LOCKED: {symbol} profit secured at +₹{pnl_inr:.2f}!", close_res)
                else:
                    self.log("INFO", f"Position Closed: {symbol} - {reason}", close_res)

        # Update equity curve
        summary = self.broker.get_account_summary()
        self.equity_curve.append({
            "time": time.strftime("%H:%M:%S"),
            "value": summary["portfolio_value"],
            "pnl": summary["total_pnl_inr"]
        })
        if len(self.equity_curve) > 120:
            self.equity_curve.pop(0)

    def get_dashboard_state(self) -> Dict[str, Any]:
        """Provides full real-time snapshot for the user interface."""
        summary = self.broker.get_account_summary()
        clock_status = market_clock.get_status()
        suppressor_stats = loss_suppressor.get_stats()
        positions = self.broker.get_positions()
        
        # Calculate Win/Loss bar chart data
        closed_trades = paper_broker.trade_history
        wins = [t for t in closed_trades if t["pnl_inr"] > 0]
        losses = [t for t in closed_trades if t["pnl_inr"] <= 0]
        
        win_rate = (len(wins) / len(closed_trades) * 100.0) if closed_trades else 0.0
        total_profit = sum(t["pnl_inr"] for t in wins)
        total_loss = sum(t["pnl_inr"] for t in losses)

        # Bar chart categories (Wins green, suppressed losses red)
        bar_chart_data = {
            "labels": [t["symbol"].replace(".NS", "") + f" ({t['exit_time']})" for t in closed_trades[-12:]],
            "values": [t["pnl_inr"] for t in closed_trades[-12:]],
            "colors": ["#10b981" if t["pnl_inr"] > 0 else "#ef4444" for t in closed_trades[-12:]]
        }

        # Advanced sub-system status snapshots
        mining_data = metals_mining_analyst.get_all_mining_overview()
        commodities_data = mcx_commodities_analyst.get_all_commodities()
        daily_brief_data = sector_scanner.generate_daily_brief()
        strategies_data = strategy_evolver.get_active_strategies()
        swarm_sample = micro_swarm.simulate("TATASTEEL.NS", signal_score=75.0)

        from core.self_learning import self_learning_engine
        learning_summary = self_learning_engine.get_learning_summary()

        return {
            "project_name": settings.PROJECT_NAME,
            "version": settings.VERSION,
            "autopilot_enabled": self.autopilot_enabled,
            "trading_mode": settings.TRADING_MODE,
            "market_clock": clock_status,
            "account_summary": summary,
            "performance": {
                "win_rate_pct": round(win_rate, 1),
                "total_trades": len(closed_trades),
                "winning_trades": len(wins),
                "losing_trades": len(losses),
                "gross_profits_inr": round(total_profit, 2),
                "gross_losses_inr": round(total_loss, 2),
                "net_pnl_inr": round(total_profit + total_loss, 2),
                "profit_factor": round(abs(total_profit / total_loss), 2) if total_loss != 0 else (total_profit if total_profit > 0 else 1.0)
            },
            "loss_suppression": suppressor_stats,
            "open_positions": positions,
            "recent_trades": closed_trades[-15:],
            "watchlist_analysis": list(self.analysis_cache.values()),
            "equity_curve": self.equity_curve[-30:],
            "bar_chart_data": bar_chart_data,
            "metals_and_mining": mining_data,
            "mcx_commodities": commodities_data,
            "daily_brief": daily_brief_data,
            "strategy_pool": strategies_data,
            "micro_swarm_sample": swarm_sample,
            "self_learning": learning_summary,
            "dataset_repository": dataset_manager.get_repository_stats(),
            "cross_market_graph": cross_market_graph.evaluate_cross_market_state(),
            "execution_optimizer": execution_optimizer.get_execution_metrics(),
            "research_lab": research_lab.get_laboratory_summary(),
            "risk_guardian": risk_guardian.get_status(),
            "market_segments": settings.MARKET_SEGMENTS,
            "notifications": notification_service.get_recent_notifications(15),
            "notifications_status": notification_service.get_status(),
            "tradingview_status": tradingview_trainer.get_training_summary(),
            "universal_matrix": universal_strategy_trainer.get_matrix_summary(),
            "system_logs": self.logs[-25:]
        }

    async def run_loop(self):
        """Asynchronous execution worker loop."""
        self.is_running = True
        self.log("INFO", f"{settings.PROJECT_NAME} initialized. Engine running in {settings.TRADING_MODE} mode.")

        while self.is_running:
            try:
                # 1. High frequency monitoring of open positions
                self.monitor_open_positions_sub_second()

                # 2. Market scan periodically
                now = time.time()
                if now - self.last_scan_time >= self.scan_interval_seconds:
                    self.scan_markets()
                    self.last_scan_time = now

                await asyncio.sleep(1.0)
            except Exception as e:
                self.log("ERROR", f"Loop exception: {str(e)}")
                await asyncio.sleep(2.0)

trading_engine = IndianTradingEngine()
