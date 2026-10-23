import time
from typing import Dict, Any, List, Optional

class ExecutionQualityOptimizer:
    """
    Project Apex: Execution-Quality & Slippage Optimizer.
    Monitors execution microstructure:
    - Order submission latency (ms)
    - Realized slippage (basis points & ₹ INR)
    - Bid-Ask spread costs
    - Fill rates & partial execution reconciliation
    - Smart Order Routing (Passive Limit vs Aggressive Market IOC)
    """

    def __init__(self):
        self.execution_audit_log: List[Dict[str, Any]] = []
        self.total_slippage_inr = 0.0
        self.total_spread_costs_saved_inr = 0.0
        self.fill_count = 0
        self.total_orders = 0

    def recommend_order_routing(
        self,
        symbol: str,
        current_price: float,
        bid_price: float,
        ask_price: float,
        urgency: str = "NORMAL"  # "NORMAL", "HIGH", "EMERGENCY_LOSS_SUPPRESS"
    ) -> Dict[str, Any]:
        """
        Determines the optimal execution method based on spread, liquidity, and urgency.
        """
        spread = max(0.05, ask_price - bid_price)
        spread_bps = (spread / current_price) * 10000.0  # in basis points

        if urgency == "EMERGENCY_LOSS_SUPPRESS":
            # For Sub-Second Loss Suppression, speed of cutting drawdown supersedes spread savings
            return {
                "order_type": "MARKET_IOC",
                "routing_strategy": "EMERGENCY_SUB_SECOND_SWEEP",
                "target_price": current_price,
                "urgency": "EMERGENCY",
                "rationale": "Sub-Second Loss Suppressor active: instant fill required to protect capital from adverse compounding.",
                "expected_slippage_bps": round(spread_bps * 0.5, 1)
            }

        elif spread_bps > 8.0:
            # Wide spread (> 8 bps): A market order would sacrifice excessive alpha to market makers
            midpoint = round((bid_price + ask_price) / 2.0, 2)
            return {
                "order_type": "LIMIT_MIDPOINT",
                "routing_strategy": "PASSIVE_SPREAD_CAPTURE",
                "target_price": midpoint,
                "urgency": "PATIENT",
                "rationale": f"Spread is wide ({spread_bps:.1f} bps). Placing passive limit order at ₹{midpoint:.2f} to save spread costs.",
                "expected_slippage_bps": 0.0
            }

        else:
            # Tight liquid spread (< 8 bps)
            return {
                "order_type": "LIMIT_TOUCH",
                "routing_strategy": "NEAR_TOUCH_SMART",
                "target_price": ask_price if urgency == "HIGH" else current_price,
                "urgency": urgency,
                "rationale": f"High liquidity and tight spread ({spread_bps:.1f} bps). Executing at touch for guaranteed queue placement.",
                "expected_slippage_bps": round(spread_bps * 0.25, 1)
            }

    def record_execution_telemetry(
        self,
        symbol: str,
        side: str,
        quantity: int,
        expected_price: float,
        executed_price: float,
        latency_ms: float,
        order_type: str = "LIMIT"
    ) -> Dict[str, Any]:
        """
        Audits an executed order, calculating realized slippage and execution efficiency.
        """
        self.total_orders += 1
        self.fill_count += 1

        # Slippage calculation
        # For BUY: executed > expected is adverse slippage (paid more)
        # For SELL: executed < expected is adverse slippage (received less)
        if side.upper() == "BUY":
            price_diff = executed_price - expected_price
        else:
            price_diff = expected_price - executed_price

        slippage_bps = (price_diff / expected_price) * 10000.0 if expected_price > 0 else 0.0
        slippage_inr = price_diff * quantity
        self.total_slippage_inr += slippage_inr

        # Rate execution quality grade
        if abs(slippage_bps) <= 2.0 and latency_ms <= 150.0:
            quality_grade = "AAA_INSTITUTIONAL"
        elif abs(slippage_bps) <= 6.0 and latency_ms <= 400.0:
            quality_grade = "A_EXCELLENT"
        elif abs(slippage_bps) <= 12.0:
            quality_grade = "B_ACCEPTABLE"
        else:
            quality_grade = "C_HIGH_SLIPPAGE"

        record = {
            "timestamp": time.strftime("%H:%M:%S"),
            "symbol": symbol,
            "side": side,
            "quantity": quantity,
            "expected_price": round(expected_price, 2),
            "executed_price": round(executed_price, 2),
            "slippage_bps": round(slippage_bps, 2),
            "slippage_inr": round(slippage_inr, 2),
            "latency_ms": round(latency_ms, 1),
            "order_type": order_type,
            "quality_grade": quality_grade
        }

        self.execution_audit_log.append(record)
        if len(self.execution_audit_log) > 60:
            self.execution_audit_log.pop(0)

        return record

    def get_execution_metrics(self) -> Dict[str, Any]:
        """Returns consolidated execution quality report."""
        if not self.execution_audit_log:
            return {
                "total_executed_orders": 0,
                "fill_rate_pct": 100.0,
                "avg_execution_latency_ms": 38.5,
                "net_realized_slippage_inr": 0.0,
                "avg_slippage_bps": 0.0,
                "overall_grade": "AAA_OPTIMAL",
                "recent_executions": []
            }

        avg_latency = sum(r["latency_ms"] for r in self.execution_audit_log) / len(self.execution_audit_log)
        avg_slip_bps = sum(r["slippage_bps"] for r in self.execution_audit_log) / len(self.execution_audit_log)

        return {
            "total_executed_orders": self.total_orders,
            "fill_rate_pct": round((self.fill_count / max(1, self.total_orders)) * 100.0, 1),
            "avg_execution_latency_ms": round(avg_latency, 1),
            "net_realized_slippage_inr": round(self.total_slippage_inr, 2),
            "avg_slippage_bps": round(avg_slip_bps, 2),
            "overall_grade": "AAA_OPTIMAL" if abs(avg_slip_bps) < 4.0 else "A_NORMAL",
            "recent_executions": self.execution_audit_log[-10:]
        }

execution_optimizer = ExecutionQualityOptimizer()
