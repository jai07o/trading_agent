import uvicorn
import os
import sys
from config.settings import settings

# Ensure UTF-8 output on Windows consoles
if sys.stdout.encoding != 'utf-8':
    try:
        sys.stdout.reconfigure(encoding='utf-8', errors='replace')
        sys.stderr.reconfigure(encoding='utf-8', errors='replace')
    except Exception:
        pass

def main():
    banner = f"""
    \033[93m  ____  _   _    _    ____      _  _____   _____ ____      _    ____  _____ ____  
     | __ )| | | |  / \\  |  _ \\    / \\|_   _| |_   _|  _ \\    / \\  |  _ \\| ____|  _ \\ 
     |  _ \\| |_| | / _ \\ | |_) |  / _ \\ | |     | | | |_) |  / _ \\ | | | |  _| | |_) |
     | |_) |  _  |/ ___ \\|  _ <  / ___ \\| |     | | |  _ <  / ___ \\| |_| | |___|  _ < 
     |____/|_| |_/_/   \\_\\_| \\_\\/_/   \\_\\_|     |_| |_| \\_\\/_/   \\_\\____/|_____|_| \\_\\
    \033[96m  🐅 [ BHARAT TIGER ] ━━━━━▲ 24/7 APEX QUANTITATIVE TRADING ▲━━━━━ [ APEX BULL ] 🐂\033[0m
    ====================================================================================
       * \033[97mEngine Mode:\033[0m         {settings.TRADING_MODE}
       * \033[92mSub-Second Guard:\033[0m    ACTIVE (Instant Loss Suppressor @ -0.4% / -0.5%)
       * \033[92mDynamic Profit Lock:\033[0m ENABLED (Tiered Trailing Exits)
       * \033[93mProject Apex:\033[0m        Cross-Market, Model Disagreement, Risk Guardian
       * \033[97mIndian Currency:\033[0m     INR (Native ₹)
       * \033[96mDatasets Vault:\033[0m      7 Comprehensive Market & Macro Datasets
       * \033[94mLocal Dashboard:\033[0m     http://localhost:{settings.PORT}
    ====================================================================================
    """
    print(banner)
    print(f"[*] Starting BharatTrader AI background engine & web dashboard on port {settings.PORT}...")
    
    uvicorn.run(
        "server.api:app",
        host=settings.HOST,
        port=settings.PORT,
        log_level="info",
        reload=False
    )

if __name__ == "__main__":
    main()
