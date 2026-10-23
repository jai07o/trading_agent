import os
from pydantic import BaseModel
from typing import List, Dict, Any
from dotenv import load_dotenv

load_dotenv()

class TradingSettings(BaseModel):
    PROJECT_NAME: str = "BharatTrader AI"
    VERSION: str = "2.5.0"
    
    # Mode: 'PAPER' or 'LIVE'
    TRADING_MODE: str = os.getenv("TRADING_MODE", "PAPER").upper()
    
    # Capital & Currency (INR)
    STARTING_CAPITAL_INR: float = float(os.getenv("STARTING_CAPITAL_INR", "100000.0"))
    CURRENCY_SYMBOL: str = "₹"
    
    # Comprehensive Indian Market Segments
    MARKET_SEGMENTS: Dict[str, List[str]] = {
        "METALS_AND_MINING": [
            "TATASTEEL.NS",   # Tata Steel Ltd
            "JSWSTEEL.NS",    # JSW Steel Ltd
            "HINDALCO.NS",    # Hindalco Industries (Aluminium/Copper)
            "COALINDIA.NS",   # Coal India Ltd (Largest Coal Miner)
            "VEDL.NS",        # Vedanta Ltd (Zinc, Lead, Silver, Iron Ore)
            "NMDC.NS",        # National Mineral Development Corp (Iron Ore)
            "HINDZINC.NS",    # Hindustan Zinc Ltd (Top Silver/Zinc Miner)
            "SAIL.NS",        # Steel Authority of India
            "JINDALSTEL.NS"   # Jindal Steel & Power
        ],
        "COMMODITIES_MCX": [
            "GOLD_MCX",       # MCX Gold 1kg / Mini
            "SILVER_MCX",     # MCX Silver 30kg / Mini
            "CRUDEOIL_MCX",   # MCX Crude Oil
            "COPPER_MCX",     # MCX Copper
            "NATGAS_MCX"      # MCX Natural Gas
        ],
        "EQUITIES_CORE": [
            "NIFTY50",
            "BANKNIFTY",
            "FINNIFTY",
            "RELIANCE.NS",
            "TCS.NS",
            "HDFCBANK.NS",
            "INFY.NS",
            "ICICIBANK.NS",
            "TATAMOTORS.NS",
            "SBIN.NS",
            "BHARTIARTL.NS",
            "ITC.NS",
            "LT.NS"
        ],
        "CRYPTO_MACRO": [
            "BTC-INR",
            "ETH-INR",
            "USDINR"
        ]
    }
    
    # Default combined watchlist
    PRIMARY_WATCHLIST: List[str] = [
        "NIFTY50",
        "BANKNIFTY",
        "TATASTEEL.NS",
        "COALINDIA.NS",
        "VEDL.NS",
        "NMDC.NS",
        "GOLD_MCX",
        "CRUDEOIL_MCX",
        "RELIANCE.NS",
        "TCS.NS",
        "HDFCBANK.NS"
    ]
    
    # Indian Market Hours (IST)
    MARKET_OPEN_HOUR: int = 9
    MARKET_OPEN_MINUTE: int = 15
    MARKET_CLOSE_HOUR: int = 15
    MARKET_CLOSE_MINUTE: int = 30
    INTRADAY_SQUAREOFF_HOUR: int = 15
    INTRADAY_SQUAREOFF_MINUTE: int = 15
    
    # MCX Commodity Evening Session Hours (IST)
    MCX_OPEN_HOUR: int = 9
    MCX_OPEN_MINUTE: int = 0
    MCX_CLOSE_HOUR: int = 23
    MCX_CLOSE_MINUTE: int = 30
    
    # Sub-Second Loss Suppression & Profit Lock Settings
    LOSS_SUPPRESS_THRESHOLD_PCT: float = 0.50      # Auto-cut when trade is -0.50% down in fraction of a second
    HARD_STOP_LOSS_PCT: float = 0.80               # Hard absolute stop loss
    TRAILING_STOP_ACTIVATION_PCT: float = 0.75     # Activate trailing stop once +0.75% profit reached
    TRAILING_STEP_PCT: float = 0.35                # Trailing buffer
    MAX_DAILY_DRAWDOWN_PCT: float = 2.5            # Emergency circuit breaker for the day
    
    # Dynamic Profit Lock Tiers (Locking profits as price rises)
    PROFIT_LOCK_TIERS: List[Dict[str, float]] = [
        {"gain": 1.0, "lock": 0.5},
        {"gain": 2.0, "lock": 1.4},
        {"gain": 3.0, "lock": 2.4},
        {"gain": 5.0, "lock": 4.2}
    ]
    
    # Risk Management & Position Sizing
    MAX_OPEN_POSITIONS: int = 6
    MAX_ALLOCATION_PER_TRADE_PCT: float = 18.0     # Max 18% of capital in single stock
    KELLY_FRACTION: float = 0.40                   # Half-Kelly for capital preservation
    
    # Broker Configuration (Angel One SmartAPI - Free Tier)
    ANGEL_API_KEY: str = os.getenv("ANGEL_API_KEY", "")
    ANGEL_CLIENT_ID: str = os.getenv("ANGEL_CLIENT_ID", "")
    ANGEL_PIN: str = os.getenv("ANGEL_PIN", "")
    ANGEL_TOTP_KEY: str = os.getenv("ANGEL_TOTP_KEY", "")
    
    # Multi-Provider AI LLM Configuration
    ORALEXXA_LLM_PROVIDER: str = os.getenv("ORALEXXA_LLM_PROVIDER", "GEMINI").upper() # GEMINI, CLAUDE, OPENAI, OLLAMA
    GEMINI_API_KEY: str = os.getenv("GEMINI_API_KEY", "")
    ANTHROPIC_API_KEY: str = os.getenv("ANTHROPIC_API_KEY", "")
    OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY", "")
    OLLAMA_BASE_URL: str = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
    
    # Server & Dashboard Ports
    PORT: int = int(os.getenv("PORT", "8585"))
    HOST: str = os.getenv("HOST", "0.0.0.0")

settings = TradingSettings()
