import datetime
import pytz
from typing import Dict, Any

class IndianMarketClock:
    """
    Manages Indian Stock Market (NSE/BSE) trading hours in Indian Standard Time (IST).
    Market hours: 09:15 AM to 03:30 PM IST, Monday through Friday.
    Intraday square-off begins at 03:15 PM IST.
    """
    
    def __init__(self):
        self.tz = pytz.timezone("Asia/Kolkata")
        
    def get_current_ist_time(self) -> datetime.datetime:
        """Returns the current datetime in Indian Standard Time (IST)."""
        return datetime.datetime.now(self.tz)
    
    def is_trading_day(self, now: datetime.datetime = None) -> bool:
        """Checks if today is a weekday (Monday=0 to Friday=4)."""
        if now is None:
            now = self.get_current_ist_time()
        return now.weekday() < 5
    
    def is_market_open(self, now: datetime.datetime = None) -> bool:
        """
        Determines whether regular trading is currently active (09:15 - 15:30 IST).
        """
        if now is None:
            now = self.get_current_ist_time()
            
        if not self.is_trading_day(now):
            return False
            
        market_open = now.replace(hour=9, minute=15, second=0, microsecond=0)
        market_close = now.replace(hour=15, minute=30, second=0, microsecond=0)
        
        return market_open <= now <= market_close
    
    def is_intraday_squareoff_time(self, now: datetime.datetime = None) -> bool:
        """Checks if it's 3:15 PM IST or later, when intraday positions must be closed."""
        if now is None:
            now = self.get_current_ist_time()
            
        if not self.is_trading_day(now):
            return False
            
        squareoff_time = now.replace(hour=15, minute=15, second=0, microsecond=0)
        market_close = now.replace(hour=15, minute=30, second=0, microsecond=0)
        
        return squareoff_time <= now <= market_close

    def is_mcx_open(self, now: datetime.datetime = None) -> bool:
        """Checks if MCX Commodity session is currently active (09:00 - 23:30 IST)."""
        if now is None:
            now = self.get_current_ist_time()
        if not self.is_trading_day(now):
            return False
        mcx_open = now.replace(hour=9, minute=0, second=0, microsecond=0)
        mcx_close = now.replace(hour=23, minute=30, second=0, microsecond=0)
        return mcx_open <= now <= mcx_close

    def get_24_7_session(self, now: datetime.datetime = None) -> Dict[str, Any]:
        """Provides 24/7 continuous operational session metadata across all global regimes."""
        if now is None:
            now = self.get_current_ist_time()
        
        is_weekday = self.is_trading_day(now)
        hour = now.hour
        minute = now.minute
        time_decimal = hour + minute / 60.0

        if is_weekday and (9.25 <= time_decimal <= 15.5):
            return {
                "active_market": "NSE / BSE EQUITIES & METALS/MINING",
                "phase": "LIVE_EQUITY_INTRADAY",
                "risk_profile": "ACTIVE_SUB_SECOND_GUARD",
                "status_text": "NSE/BSE REGULAR SESSION LIVE",
                "color": "#10B981"
            }
        elif is_weekday and (17.0 <= time_decimal <= 23.5):
            return {
                "active_market": "MCX COMMODITIES (GOLD, SILVER, CRUDE, COPPER)",
                "phase": "LIVE_MCX_EVENING_SESSION",
                "risk_profile": "COMMODITY_VOLATILITY_GUARD",
                "status_text": "MCX EVENING COMMODITY SESSION LIVE",
                "color": "#F59E0B"
            }
        else:
            return {
                "active_market": "OVERNIGHT GLOBAL MACRO, CRYPTO 24/7 & AI SELF-TRAINING",
                "phase": "CONTINUOUS_24_7_LEARNING_AND_HEDGING",
                "risk_profile": "CAPITAL_PRESERVATION_AND_MODEL_TRAINING",
                "status_text": "24/7 GLOBAL MACRO & AI SELF-TRAINING LIVE",
                "color": "#3B82F6"
            }

    def get_status(self) -> Dict[str, Any]:
        """Provides full real-time status of Indian and 24/7 global market state."""
        now = self.get_current_ist_time()
        is_open = self.is_market_open(now)
        is_squareoff = self.is_intraday_squareoff_time(now)
        session_24_7 = self.get_24_7_session(now)
        
        time_str = now.strftime("%I:%M:%S %p IST")
        date_str = now.strftime("%d-%b-%Y (%A)")
        
        return {
            "current_time": time_str,
            "current_date": date_str,
            "timezone": "Asia/Kolkata",
            "is_open": is_open,
            "is_squareoff": is_squareoff,
            "is_24_7_live": True,
            "session": session_24_7["status_text"],
            "session_24_7": session_24_7,
            "exchange": session_24_7["active_market"]
        }

market_clock = IndianMarketClock()
