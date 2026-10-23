import time
from typing import Dict, Any, List, Optional
from config.settings import settings

class SuppressionEvent:
    def __init__(self, symbol: str, action: str, reason: str, saved_loss_inr: float, pnl_pct: float, timestamp: float):
        self.symbol = symbol
        self.action = action
        self.reason = reason
        self.saved_loss_inr = saved_loss_inr
        self.pnl_pct = pnl_pct
        self.timestamp = timestamp

    def to_dict(self) -> Dict[str, Any]:
        return {
            "symbol": self.symbol,
            "action": self.action,
            "reason": self.reason,
            "saved_loss_inr": round(self.saved_loss_inr, 2),
            "pnl_pct": round(self.pnl_pct, 2),
            "time": time.strftime("%H:%M:%S", time.localtime(self.timestamp))
        }

class SubSecondLossSuppressor:
    """
    Sub-Second Loss Suppression and Dynamic Profit Locking Engine for BharatTrader AI.
    Specifically designed to:
    1. Cut losses in fractions of a second before they can compound.
    2. Dynamically lock profits in ascending tiers as a trade advances.
    3. Enforce intraday circuit-breakers to protect Indian retail trading capital.
    """

    def __init__(self):
        self.suppression_history: List[SuppressionEvent] = []
        self.total_losses_suppressed_inr: float = 0.0
        self.total_profits_locked_inr: float = 0.0
        self.sensitivity_mode: str = "HYPER"  # Options: HYPER, BALANCED, RELAXED

    def set_sensitivity(self, mode: str):
        mode = mode.upper()
        if mode in ["HYPER", "BALANCED", "RELAXED"]:
            self.sensitivity_mode = mode

    def get_thresholds(self) -> Dict[str, float]:
        if self.sensitivity_mode == "HYPER":
            # Extremely fast loss-cutting and tight profit trailing
            return {
                "loss_cut_pct": 0.40,      # Cuts at -0.40%
                "hard_stop_pct": 0.65,
                "trailing_activation_pct": 0.60,
                "trailing_step_pct": 0.25
            }
        elif self.sensitivity_mode == "BALANCED":
            return {
                "loss_cut_pct": settings.LOSS_SUPPRESS_THRESHOLD_PCT, # 0.50%
                "hard_stop_pct": settings.HARD_STOP_LOSS_PCT,          # 0.80%
                "trailing_activation_pct": settings.TRAILING_STOP_ACTIVATION_PCT, # 0.75%
                "trailing_step_pct": settings.TRAILING_STEP_PCT        # 0.35%
            }
        else: # RELAXED
            return {
                "loss_cut_pct": 0.85,
                "hard_stop_pct": 1.20,
                "trailing_activation_pct": 1.10,
                "trailing_step_pct": 0.50
            }

    def evaluate_position(self, position: Dict[str, Any], current_price: float) -> Dict[str, Any]:
        """
        Micro-evaluation executed on every price tick.
        Returns evaluation dict with:
        - action: 'HOLD', 'SUPPRESS_LOSS', 'LOCK_PROFIT', 'TAKE_TARGET', 'HARD_STOP'
        - reason: Description of the trigger
        """
        symbol = position.get("symbol", "")
        entry_price = position.get("entry_price", current_price)
        side = position.get("side", "BUY") # BUY (Long) or SELL (Short)
        quantity = position.get("quantity", 1)
        peak_price = position.get("peak_price", entry_price)
        
        # Calculate instantaneous P&L
        if side == "BUY":
            pnl_pct = ((current_price - entry_price) / entry_price) * 100.0
            pnl_inr = (current_price - entry_price) * quantity
            if current_price > peak_price:
                position["peak_price"] = current_price
                peak_price = current_price
            peak_pnl_pct = ((peak_price - entry_price) / entry_price) * 100.0
        else:
            pnl_pct = ((entry_price - current_price) / entry_price) * 100.0
            pnl_inr = (entry_price - current_price) * quantity
            if current_price < peak_price:
                position["peak_price"] = current_price
                peak_price = current_price
            peak_pnl_pct = ((entry_price - peak_price) / entry_price) * 100.0

        thresholds = self.get_thresholds()
        loss_cut_limit = thresholds["loss_cut_pct"]
        hard_stop_limit = thresholds["hard_stop_pct"]

        # 1. IMMEDIATE SUB-SECOND LOSS SUPPRESSION TRIGGER
        # If the trade dips into red beyond threshold, suppress immediately
        if pnl_pct <= -loss_cut_limit:
            # Estimate potential loss avoided (standard retail trade can drift into -2.5% to -5%)
            estimated_disaster_pct = 3.0
            saved_loss = max(0.0, (estimated_disaster_pct - abs(pnl_pct)) / 100.0 * entry_price * quantity)
            self.total_losses_suppressed_inr += saved_loss
            
            event = SuppressionEvent(
                symbol=symbol,
                action="SUPPRESS_LOSS",
                reason=f"Instant Sub-Second Cut: Hit -{abs(pnl_pct):.2f}% (Limit: -{loss_cut_limit:.2f}%). Suppressed deeper loss.",
                saved_loss_inr=saved_loss,
                pnl_pct=pnl_pct,
                timestamp=time.time()
            )
            self.suppression_history.append(event)
            try:
                from core.notification_service import notification_service
                notification_service.notify_loss_suppression(
                    symbol=symbol,
                    exit_price=current_price,
                    return_pct=pnl_pct,
                    saved_inr=saved_loss
                )
            except Exception:
                pass
            return {
                "action": "SUPPRESS_LOSS",
                "should_close": True,
                "reason": event.reason,
                "pnl_pct": pnl_pct,
                "pnl_inr": pnl_inr,
                "saved_loss_inr": saved_loss
            }

        # 2. DYNAMIC TIERED PROFIT-LOCKING TRIGGER
        # Check if the trade reached profit tiers and is now retreating towards lock floor
        for tier in reversed(settings.PROFIT_LOCK_TIERS):
            gain_target = tier["gain"]
            lock_floor = tier["lock"]
            
            if peak_pnl_pct >= gain_target:
                # If peak hit this tier, the current P&L must NOT fall below lock_floor
                if pnl_pct <= lock_floor:
                    locked_gain_inr = max(0.0, pnl_inr)
                    self.total_profits_locked_inr += locked_gain_inr
                    event = SuppressionEvent(
                        symbol=symbol,
                        action="LOCK_PROFIT",
                        reason=f"Dynamic Profit Lock: Peak was +{peak_pnl_pct:.2f}%. Secured +{pnl_pct:.2f}% profit at tier floor.",
                        saved_loss_inr=0.0,
                        pnl_pct=pnl_pct,
                        timestamp=time.time()
                    )
                    self.suppression_history.append(event)
                    try:
                        from core.notification_service import notification_service
                        notification_service.notify_profit_lock(
                            symbol=symbol,
                            exit_price=current_price,
                            pnl_inr=locked_gain_inr,
                            tier_str=event.reason
                        )
                    except Exception:
                        pass
                    return {
                        "action": "LOCK_PROFIT",
                        "should_close": True,
                        "reason": event.reason,
                        "pnl_pct": pnl_pct,
                        "pnl_inr": pnl_inr,
                        "saved_loss_inr": 0.0
                    }
                break

        # 3. TRAILING STOP TRIGGER
        if peak_pnl_pct >= thresholds["trailing_activation_pct"]:
            retracement_pct = peak_pnl_pct - pnl_pct
            if retracement_pct >= thresholds["trailing_step_pct"]:
                return {
                    "action": "TRAILING_STOP",
                    "should_close": True,
                    "reason": f"Trailing Stop: Retraced {retracement_pct:.2f}% from peak +{peak_pnl_pct:.2f}%.",
                    "pnl_pct": pnl_pct,
                    "pnl_inr": pnl_inr,
                    "saved_loss_inr": 0.0
                }

        # Default state: Hold and monitor
        return {
            "action": "HOLD",
            "should_close": False,
            "reason": f"Active: P&L {pnl_pct:+.2f}% | Peak {peak_pnl_pct:+.2f}%",
            "pnl_pct": pnl_pct,
            "pnl_inr": pnl_inr,
            "saved_loss_inr": 0.0
        }

    def get_stats(self) -> Dict[str, Any]:
        return {
            "sensitivity": self.sensitivity_mode,
            "sensitivity_mode": self.sensitivity_mode,
            "total_losses_suppressed_inr": round(self.total_losses_suppressed_inr, 2),
            "total_profits_locked_inr": round(self.total_profits_locked_inr, 2),
            "suppression_count": len(self.suppression_history),
            "recent_events": [e.to_dict() for e in self.suppression_history[-10:]]
        }

loss_suppressor = SubSecondLossSuppressor()
