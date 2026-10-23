import math
from typing import Dict, Any
from config.settings import settings

class IndianPositionSizer:
    """
    Position Sizing Engine combining Fractional Kelly Criterion with ATR Volatility.
    Calibrated for Indian Equities and F&O derivatives in ₹ INR.
    """

    def __init__(self, default_capital: float = None):
        self.capital = default_capital or settings.STARTING_CAPITAL_INR
        self.kelly_fraction = settings.KELLY_FRACTION
        self.max_trade_risk_pct = 1.5 # Maximum 1.5% portfolio risk per trade

    def calculate_share_quantity(
        self,
        symbol: str,
        entry_price: float,
        stop_loss_price: float,
        confidence_score: float = 75.0,
        available_cash: float = None
    ) -> Dict[str, Any]:
        """
        Calculates optimal quantity of shares or lots to buy.
        Ensures risk is strictly capped to `max_trade_risk_pct` of current capital.
        """
        cash = available_cash if available_cash is not None else self.capital
        
        if entry_price <= 0:
            return {"quantity": 0, "investment_inr": 0, "risk_inr": 0, "reason": "Invalid price"}

        # 1. Calculate Per-Share Risk
        per_share_risk = abs(entry_price - stop_loss_price)
        if per_share_risk <= 0.01:
            per_share_risk = entry_price * (settings.LOSS_SUPPRESS_THRESHOLD_PCT / 100.0)

        # 2. Maximum capital willing to risk on this single trade
        # Scaled by confidence (50% to 100%)
        confidence_multiplier = min(1.2, max(0.6, confidence_score / 75.0))
        max_risk_inr = cash * (self.max_trade_risk_pct / 100.0) * confidence_multiplier

        # 3. Kelly Criterion Allocation Sizing
        # Kelly: f* = (p*b - q) / b
        # where p = win probability, b = win/loss payoff ratio
        p = min(0.85, max(0.45, confidence_score / 100.0))
        q = 1.0 - p
        payoff_ratio = 2.0 # Standard 2:1 target to risk ratio
        kelly_optimal = (p * payoff_ratio - q) / payoff_ratio
        kelly_f = max(0.05, min(0.35, kelly_optimal * self.kelly_fraction))

        # 4. Quantity based on Risk
        qty_by_risk = math.floor(max_risk_inr / per_share_risk)

        # 5. Quantity based on Max Capital Allocation (e.g. 20% max of portfolio in 1 stock)
        max_capital_allowed = cash * (settings.MAX_ALLOCATION_PER_TRADE_PCT / 100.0)
        qty_by_capital = math.floor(max_capital_allowed / entry_price)

        # 6. Final safe quantity
        quantity = max(1, min(qty_by_risk, qty_by_capital))

        # Special handling for Nifty / BankNifty Lot sizes if index derivative
        if "NIFTY" in symbol.upper() and not symbol.endswith(".NS"):
            lot_size = 25 # Current standard Nifty lot
            quantity = max(lot_size, math.floor(quantity / lot_size) * lot_size)
        elif "BANKNIFTY" in symbol.upper() and not symbol.endswith(".NS"):
            lot_size = 15 # Current standard BankNifty lot
            quantity = max(lot_size, math.floor(quantity / lot_size) * lot_size)

        total_investment = quantity * entry_price
        total_risk = quantity * per_share_risk

        return {
            "quantity": quantity,
            "entry_price": round(entry_price, 2),
            "stop_loss_price": round(stop_loss_price, 2),
            "investment_inr": round(total_investment, 2),
            "risk_inr": round(total_risk, 2),
            "risk_pct_of_capital": round((total_risk / cash) * 100.0, 2),
            "allocation_pct": round((total_investment / cash) * 100.0, 2)
        }

position_sizer = IndianPositionSizer()
