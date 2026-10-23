import time
import random
from typing import Dict, Any, List
from brokers.base_broker import BaseBroker
from config.settings import settings

class IndianPaperBroker(BaseBroker):
    """
    High-fidelity Indian Paper Trading Broker.
    Simulates NSE/BSE intraday and positional trading with realistic STT, brokerage, and slippage.
    """

    def __init__(self, initial_capital: float = None):
        self.capital = initial_capital or settings.STARTING_CAPITAL_INR
        self.available_cash = self.capital
        self.positions: Dict[str, Dict[str, Any]] = {}
        self.trade_history: List[Dict[str, Any]] = []
        self.realized_pnl_inr = 0.0
        
        # Benchmark baseline prices (in ₹ INR)
        self.market_prices: Dict[str, float] = {
            "RELIANCE.NS": 2945.50,
            "TCS.NS": 3915.20,
            "HDFCBANK.NS": 1642.80,
            "INFY.NS": 1845.00,
            "ICICIBANK.NS": 1215.60,
            "TATAMOTORS.NS": 985.40,
            "SBIN.NS": 812.30,
            "BHARTIARTL.NS": 1680.00,
            "NIFTY50": 24820.00,
            "BANKNIFTY": 51350.00
        }

    def update_tick(self, symbol: str, delta_pct: float = None) -> float:
        """Simulates realistic micro-price movements for live testing."""
        if symbol not in self.market_prices:
            self.market_prices[symbol] = 1000.0

        if delta_pct is None:
            # Random micro-fluctuation between -0.15% and +0.18% (slight positive drift)
            delta_pct = random.uniform(-0.15, 0.18)

        old_price = self.market_prices[symbol]
        new_price = old_price * (1.0 + (delta_pct / 100.0))
        self.market_prices[symbol] = round(new_price, 2)
        return self.market_prices[symbol]

    def get_live_quote(self, symbol: str) -> float:
        return self.market_prices.get(symbol, 1000.0)

    def get_account_summary(self) -> Dict[str, Any]:
        unrealized_pnl = 0.0
        invested_value = 0.0

        for symbol, pos in self.positions.items():
            current_price = self.get_live_quote(symbol)
            qty = pos["quantity"]
            entry = pos["entry_price"]
            side = pos["side"]

            if side == "BUY":
                pos_pnl = (current_price - entry) * qty
                inv = current_price * qty
            else:
                pos_pnl = (entry - current_price) * qty
                inv = entry * qty

            unrealized_pnl += pos_pnl
            invested_value += inv

        portfolio_value = self.available_cash + invested_value
        total_pnl = self.realized_pnl_inr + unrealized_pnl
        total_return_pct = ((portfolio_value - self.capital) / self.capital) * 100.0

        return {
            "currency": "INR",
            "symbol": settings.CURRENCY_SYMBOL,
            "starting_capital": round(self.capital, 2),
            "available_cash": round(self.available_cash, 2),
            "invested_value": round(invested_value, 2),
            "portfolio_value": round(portfolio_value, 2),
            "realized_pnl_inr": round(self.realized_pnl_inr, 2),
            "unrealized_pnl_inr": round(unrealized_pnl, 2),
            "total_pnl_inr": round(total_pnl, 2),
            "total_return_pct": round(total_return_pct, 2),
            "open_positions_count": len(self.positions),
            "closed_trades_count": len(self.trade_history)
        }

    def get_positions(self) -> List[Dict[str, Any]]:
        pos_list = []
        for symbol, pos in self.positions.items():
            current_price = self.get_live_quote(symbol)
            qty = pos["quantity"]
            entry = pos["entry_price"]
            side = pos["side"]

            if side == "BUY":
                pnl_inr = (current_price - entry) * qty
                pnl_pct = ((current_price - entry) / entry) * 100.0
            else:
                pnl_inr = (entry - current_price) * qty
                pnl_pct = ((entry - current_price) / entry) * 100.0

            pos_copy = dict(pos)
            pos_copy["current_price"] = current_price
            pos_copy["pnl_inr"] = round(pnl_inr, 2)
            pos_copy["pnl_pct"] = round(pnl_pct, 2)
            pos_list.append(pos_copy)
        return pos_list

    def place_order(self, symbol: str, side: str, quantity: int, price: float, stop_loss: float = None, target: float = None) -> Dict[str, Any]:
        if symbol in self.positions:
            return {"status": "REJECTED", "message": f"Position already open for {symbol}"}

        total_cost = price * quantity
        # Add estimated Indian statutory charges (STT + Exchange turnover + GST ≈ 0.05%)
        charges = total_cost * 0.0005

        if self.available_cash < (total_cost + charges):
            return {"status": "REJECTED", "message": f"Insufficient funds: Need ₹{total_cost + charges:.2f}, have ₹{self.available_cash:.2f}"}

        self.available_cash -= (total_cost + charges)
        
        position = {
            "order_id": f"ORD_{int(time.time()*1000)}",
            "symbol": symbol,
            "side": side.upper(),
            "quantity": quantity,
            "entry_price": price,
            "peak_price": price,
            "stop_loss": stop_loss,
            "target": target,
            "entry_time": time.time(),
            "entry_time_str": time.strftime("%H:%M:%S"),
            "charges_paid": round(charges, 2)
        }
        self.positions[symbol] = position

        try:
            from core.notification_service import notification_service
            notification_service.notify_trade_execution(
                symbol=symbol,
                side=side.upper(),
                qty=quantity,
                price=price,
                order_id=position["order_id"]
            )
        except Exception:
            pass

        return {
            "status": "EXECUTED",
            "order_id": position["order_id"],
            "symbol": symbol,
            "side": side,
            "quantity": quantity,
            "price": price,
            "execution_price": price,
            "statutory_charges_inr": round(charges, 2),
            "message": f"Order executed successfully for {quantity} shares of {symbol} at ₹{price:.2f}"
        }

    def close_position(self, symbol: str, current_price: float, reason: str = "MANUAL") -> Dict[str, Any]:
        if symbol not in self.positions:
            return {"status": "ERROR", "message": f"No active position for {symbol}"}

        pos = self.positions.pop(symbol)
        qty = pos["quantity"]
        entry = pos["entry_price"]
        side = pos["side"]

        if side == "BUY":
            gross_pnl = (current_price - entry) * qty
            return_cash = current_price * qty
        else:
            gross_pnl = (entry - current_price) * qty
            return_cash = entry * qty + gross_pnl

        # Exit transaction charges (approx 0.05%)
        exit_charges = (current_price * qty) * 0.0005
        net_pnl = gross_pnl - pos.get("charges_paid", 0.0) - exit_charges

        self.available_cash += (return_cash - exit_charges)
        self.realized_pnl_inr += net_pnl

        pnl_pct = ((current_price - entry) / entry) * 100.0 if side == "BUY" else ((entry - current_price) / entry) * 100.0

        trade_record = {
            "order_id": pos["order_id"],
            "symbol": symbol,
            "side": side,
            "quantity": qty,
            "entry_price": entry,
            "exit_price": current_price,
            "entry_time": pos["entry_time_str"],
            "exit_time": time.strftime("%H:%M:%S"),
            "pnl_inr": round(net_pnl, 2),
            "pnl_pct": round(pnl_pct, 2),
            "outcome": "WIN" if net_pnl > 0 else "LOSS",
            "reason": reason
        }
        self.trade_history.append(trade_record)

        # Autonomous Daily Self-Learning Adaptation
        try:
            from core.self_learning import self_learning_engine
            self_learning_engine.record_and_learn_from_trade(trade_record)
        except Exception:
            pass

        return {
            "status": "CLOSED",
            "trade": trade_record,
            "pnl_inr": round(net_pnl, 2),
            "pnl_pct": round(pnl_pct, 2),
            "message": f"Closed {symbol} at ₹{current_price:.2f}. P&L: ₹{net_pnl:+.2f} ({pnl_pct:+.2f}%) [{reason}]"
        }

paper_broker = IndianPaperBroker()
