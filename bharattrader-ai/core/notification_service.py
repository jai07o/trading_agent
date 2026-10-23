import time
import json
import os
import requests
from typing import Dict, Any, List, Optional
from config.settings import settings

class NotificationService:
    """
    Multi-Channel Real-Time Notification Engine for BharatTrader AI.
    Dispatches instant alerts across:
    1. Browser Real-Time Audio & Visual Toasts (via WebSocket & Web Audio API)
    2. Telegram Bot Alerts (Telegram HTTP Bot API)
    3. Discord Webhook Alerts (Rich Embeds)
    4. Custom Webhook Relay (Zapier, Slack, TradingView response)
    5. In-Memory Audited Notification Ledger with timestamps and severities
    """

    def __init__(self):
        self.telegram_bot_token: str = os.getenv("TELEGRAM_BOT_TOKEN", "")
        self.telegram_chat_id: str = os.getenv("TELEGRAM_CHAT_ID", "")
        self.discord_webhook_url: str = os.getenv("DISCORD_WEBHOOK_URL", "")
        self.webhook_relay_url: str = os.getenv("CUSTOM_WEBHOOK_URL", "")
        self.sound_enabled: bool = True
        
        self.notification_history: List[Dict[str, Any]] = [
            {
                "id": "notif_init_001",
                "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
                "severity": "INFO",
                "title": "Notification System Armed",
                "message": "BharatTrader AI multi-channel alert engine is active. Ready to dispatch Telegram, Discord, and Browser alerts.",
                "read": True
            }
        ]

    def update_settings(self, telegram_token: Optional[str] = None, telegram_chat: Optional[str] = None, 
                        discord_webhook: Optional[str] = None, sound_enabled: Optional[bool] = None) -> Dict[str, Any]:
        """Updates notification credentials dynamically."""
        if telegram_token is not None:
            self.telegram_bot_token = telegram_token
        if telegram_chat is not None:
            self.telegram_chat_id = telegram_chat
        if discord_webhook is not None:
            self.discord_webhook_url = discord_webhook
        if sound_enabled is not None:
            self.sound_enabled = sound_enabled

        return {
            "status": "SUCCESS",
            "telegram_configured": bool(self.telegram_bot_token and self.telegram_chat_id),
            "discord_configured": bool(self.discord_webhook_url),
            "sound_enabled": self.sound_enabled
        }

    def get_status(self) -> Dict[str, Any]:
        """Returns current notification configuration status and counts."""
        unread_count = sum(1 for n in self.notification_history if not n.get("read", False))
        return {
            "telegram_configured": bool(self.telegram_bot_token and self.telegram_chat_id),
            "discord_configured": bool(self.discord_webhook_url),
            "sound_enabled": self.sound_enabled,
            "total_notifications": len(self.notification_history),
            "unread_count": unread_count
        }

    def notify(self, severity: str, title: str, message: str, metadata: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Dispatches an alert to all configured channels and records in the ledger.
        Severities: 'TRADE_FILL', 'PROFIT_LOCK', 'LOSS_CUT', 'RISK_ALERT', 'INFO'
        """
        timestamp_str = time.strftime("%Y-%m-%d %H:%M:%S")
        notif_id = f"notif_{int(time.time() * 1000)}"

        record = {
            "id": notif_id,
            "timestamp": timestamp_str,
            "severity": severity,
            "title": title,
            "message": message,
            "metadata": metadata or {},
            "read": False
        }

        # Keep last 150 notifications in memory
        self.notification_history.insert(0, record)
        if len(self.notification_history) > 150:
            self.notification_history = self.notification_history[:150]

        # Dispatch async to Telegram
        if self.telegram_bot_token and self.telegram_chat_id:
            self._dispatch_telegram(severity, title, message)

        # Dispatch async to Discord
        if self.discord_webhook_url:
            self._dispatch_discord(severity, title, message, metadata)

        return record

    def notify_trade_execution(self, symbol: str, side: str, qty: int, price: float, order_id: str):
        """Notification for a live trade order fill."""
        return self.notify(
            severity="TRADE_FILL",
            title=f"⚡ Order Filled: {side} {qty}x {symbol}",
            message=f"Filled {qty} shares of {symbol} at Rs {price:.2f}. Order ID: {order_id}. Sub-second stop-loss and trailing profit lock active.",
            metadata={"symbol": symbol, "side": side, "qty": qty, "price": price, "order_id": order_id}
        )

    def notify_loss_suppression(self, symbol: str, exit_price: float, return_pct: float, saved_inr: float):
        """Notification for sub-second loss suppression shield activation."""
        return self.notify(
            severity="LOSS_CUT",
            title=f"🛡️ Loss Suppressed: {symbol}",
            message=f"Sub-second loss guard activated! Cut {symbol} instantly at Rs {exit_price:.2f} ({return_pct:.2f}%). Prevented compounding drawdown, saving Rs {saved_inr:.2f}.",
            metadata={"symbol": symbol, "exit_price": exit_price, "return_pct": return_pct, "saved_inr": saved_inr}
        )

    def notify_profit_lock(self, symbol: str, exit_price: float, pnl_inr: float, tier_str: str):
        """Notification for dynamic tiered profit lock."""
        return self.notify(
            severity="PROFIT_LOCK",
            title=f"🔒 Profit Secured: {symbol} (+Rs {pnl_inr:.2f})",
            message=f"Dynamic profit lock secured Rs {pnl_inr:.2f} profit on {symbol} at Rs {exit_price:.2f} via {tier_str}.",
            metadata={"symbol": symbol, "exit_price": exit_price, "pnl_inr": pnl_inr, "tier": tier_str}
        )

    def notify_tradingview_training(self, strategy_name: str, win_rate_before: float, win_rate_after: float, profit_factor: float):
        """Notification when agent successfully completes TradingView strategy training."""
        return self.notify(
            severity="INFO",
            title=f"🧠 TradingView AI Training Complete: {strategy_name}",
            message=f"Agent tuned from TradingView setups! Win Rate increased from {win_rate_before:.1f}% -> {win_rate_after:.1f}%. Profit Factor: {profit_factor:.2f}. Knowledge updated.",
            metadata={"strategy": strategy_name, "win_rate_before": win_rate_before, "win_rate_after": win_rate_after, "profit_factor": profit_factor}
        )

    def _dispatch_telegram(self, severity: str, title: str, message: str):
        """Sends an alert to Telegram Bot."""
        try:
            icon = "⚡"
            if severity == "PROFIT_LOCK": icon = "🔒"
            elif severity == "LOSS_CUT": icon = "🛡️"
            elif severity == "RISK_ALERT": icon = "🚨"

            text = f"{icon} *{title}*\n{message}\n_BharatTrader AI • {time.strftime('%H:%M:%S IST')}_"
            url = f"https://api.telegram.org/bot{self.telegram_bot_token}/sendMessage"
            payload = {
                "chat_id": self.telegram_chat_id,
                "text": text,
                "parse_mode": "Markdown"
            }
            requests.post(url, json=payload, timeout=3.0)
        except Exception:
            pass

    def _dispatch_discord(self, severity: str, title: str, message: str, metadata: Optional[Dict[str, Any]]):
        """Sends an alert to Discord Webhook."""
        try:
            color = 0x3B82F6  # Blue
            if severity == "PROFIT_LOCK": color = 0x10B981  # Green
            elif severity == "LOSS_CUT": color = 0xEF4444  # Red
            elif severity == "RISK_ALERT": color = 0xF59E0B  # Amber

            embed = {
                "title": title,
                "description": message,
                "color": color,
                "footer": {"text": f"BharatTrader AI • {time.strftime('%Y-%m-%d %H:%M:%S IST')}"}
            }
            requests.post(self.discord_webhook_url, json={"embeds": [embed]}, timeout=3.0)
        except Exception:
            pass

    def get_recent_notifications(self, limit: int = 25) -> List[Dict[str, Any]]:
        return self.notification_history[:limit]

    def mark_all_as_read(self):
        for n in self.notification_history:
            n["read"] = True
        return {"status": "SUCCESS"}

notification_service = NotificationService()
