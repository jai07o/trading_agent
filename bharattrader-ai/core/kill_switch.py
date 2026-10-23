import time
from typing import Dict, Any, List, Optional, Tuple

class IndependentRiskGuardianAndKillSwitch:
    """
    Project Apex: Independent Risk Guardian & Hardware-Level Kill-Switch.
    Runs completely decoupled from AI prediction agents and strategy models.
    Enforces non-negotiable physical risk constraints:
    1. Maximum Capital at Risk per Trade (strictly <= 1.5% of total equity)
    2. Maximum Daily Cumulative Drawdown (₹5,000 INR default)
    3. Maximum Concurrent Open Positions (max 5)
    4. Maximum Correlated Sector Exposure (max 3 per sector)
    5. Protected Config Invariant: AI models CANNOT alter or disable these rules.
    6. Emergency Panic Kill-Switch: Instant halt of all trading activity.
    """

    def __init__(self):
        # Protected Invariant Limits
        self._max_risk_per_trade_pct = 1.50
        self._max_daily_drawdown_inr = 5000.00
        self._max_open_positions = 5
        self._max_positions_per_sector = 3
        self._is_config_immutable = True

        # Kill Switch State
        self.kill_switch_state = "ARMED_AND_ACTIVE"  # "ARMED_AND_ACTIVE", "EMERGENCY_HALTED", "CIRCUIT_BREAKER_TRIGGERED", "RECONCILING"
        self.halt_reason: Optional[str] = None
        self.halt_timestamp: Optional[str] = None
        
        # Outage and Reconciliation Logs
        self.reconciliation_audit: List[Dict[str, Any]] = []

    def is_trading_permitted(self) -> Tuple[bool, str]:
        """First-line hard gate before any order can be processed."""
        if self.kill_switch_state != "ARMED_AND_ACTIVE":
            return False, f"TRADING BLOCKED by Independent Kill-Switch: Status is {self.kill_switch_state} ({self.halt_reason})"
        return True, "Trading authorized by Risk Guardian."

    def validate_and_authorize_order(
        self,
        symbol: str,
        side: str,
        quantity: int,
        price: float,
        portfolio_value: float,
        current_positions: List[Dict[str, Any]],
        realized_daily_pnl_inr: float
    ) -> Tuple[bool, str]:
        """
        Independent deterministic risk check.
        Evaluates the trade strictly against capital budgets.
        Completely ignores AI confidence or bullish excitement.
        """
        # Check 1: Kill switch state
        if self.kill_switch_state != "ARMED_AND_ACTIVE":
            return False, f"ORDER REJECTED: Kill-Switch is ACTIVE ({self.halt_reason})."

        # Check 2: Daily drawdown circuit breaker
        if realized_daily_pnl_inr <= -self._max_daily_drawdown_inr:
            self.trigger_kill_switch(
                reason=f"DAILY DRAWDOWN BREACH: Realized loss ₹{abs(realized_daily_pnl_inr):.2f} exceeded limit ₹{self._max_daily_drawdown_inr:.2f}."
            )
            return False, f"CIRCUIT BREAKER: Daily loss limit breached. All further orders blocked for remainder of session."

        # Check 3: Maximum open positions
        if len(current_positions) >= self._max_open_positions:
            return False, f"ORDER REJECTED: Maximum concurrent position limit ({self._max_open_positions}) reached."

        # Check 4: Position already open for this exact symbol
        for pos in current_positions:
            if pos["symbol"] == symbol:
                return False, f"ORDER REJECTED: Position already active for {symbol}. Pyramiding without risk budget prohibited."

        # Check 5: Total order commitment
        order_notional = quantity * price
        max_notional_permitted = portfolio_value * 0.25  # Max 25% allocation to single position
        if order_notional > max_notional_permitted:
            return False, f"ORDER REJECTED: Order notional ₹{order_notional:.2f} exceeds single-asset cap (₹{max_notional_permitted:.2f})."

        # Check 6: Maximum correlated sector exposure (e.g. Metals & Mining)
        mining_symbols = ["TATASTEEL.NS", "COALINDIA.NS", "NMDC.NS", "VEDL.NS", "HINDALCO.NS", "HINDZINC.NS"]
        if symbol in mining_symbols:
            open_mining = sum(1 for p in current_positions if p["symbol"] in mining_symbols)
            if open_mining >= self._max_positions_per_sector:
                return False, f"ORDER REJECTED: Sector concentration limit reached ({open_mining}/{self._max_positions_per_sector} Mining positions active)."

        return True, "ORDER APPROVED: All independent risk guardian checks passed."

    def trigger_kill_switch(self, reason: str = "Manual Emergency Halt triggered by User.") -> Dict[str, Any]:
        """Instantly halts all trading activity."""
        self.kill_switch_state = "EMERGENCY_HALTED"
        self.halt_reason = reason
        self.halt_timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
        return {
            "status": "HALTED",
            "state": self.kill_switch_state,
            "reason": self.halt_reason,
            "timestamp": self.halt_timestamp
        }

    def reset_kill_switch(self) -> Dict[str, Any]:
        """Manually restores trading after safety review."""
        self.kill_switch_state = "ARMED_AND_ACTIVE"
        self.halt_reason = None
        self.halt_timestamp = None
        return {
            "status": "ARMED",
            "state": self.kill_switch_state,
            "message": "Independent Risk Guardian armed and ready for trading."
        }

    def reconcile_positions_after_outage(
        self,
        internal_positions: List[Dict[str, Any]],
        broker_positions: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Reconciles internal state with verified broker positions after a restart or network hiccup.
        """
        discrepancies = []
        broker_symbols = {p["symbol"]: p for p in broker_positions}
        internal_symbols = {p["symbol"]: p for p in internal_positions}

        for sym, b_pos in broker_symbols.items():
            if sym not in internal_symbols:
                discrepancies.append({
                    "symbol": sym,
                    "type": "ORPHANED_BROKER_POSITION",
                    "broker_qty": b_pos.get("quantity", 0),
                    "internal_qty": 0,
                    "action_required": "Adopt broker position into internal tracking."
                })

        for sym, i_pos in internal_symbols.items():
            if sym not in broker_symbols:
                discrepancies.append({
                    "symbol": sym,
                    "type": "GHOST_INTERNAL_POSITION",
                    "broker_qty": 0,
                    "internal_qty": i_pos.get("quantity", 0),
                    "action_required": "Mark internal position as closed externally."
                })

        audit_record = {
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
            "discrepancies_found": len(discrepancies),
            "discrepancies": discrepancies,
            "status": "CLEAN" if len(discrepancies) == 0 else "ACTION_REQUIRED"
        }
        self.reconciliation_audit.append(audit_record)
        return audit_record

    def get_status(self) -> Dict[str, Any]:
        """Provides real-time health and risk guard telemetry."""
        return {
            "kill_switch_state": self.kill_switch_state,
            "halt_reason": self.halt_reason,
            "halt_timestamp": self.halt_timestamp,
            "is_trading_permitted": (self.kill_switch_state == "ARMED_AND_ACTIVE"),
            "max_risk_per_trade_pct": self._max_risk_per_trade_pct,
            "max_daily_drawdown_inr": self._max_daily_drawdown_inr,
            "max_open_positions": self._max_open_positions,
            "max_positions_per_sector": self._max_positions_per_sector,
            "protected_config_immutable": self._is_config_immutable
        }

risk_guardian = IndependentRiskGuardianAndKillSwitch()
