from typing import Dict, Any, List

class UniversalTradingKnowledgeBase:
    """
    Global Encyclopedia of All Recognized Trading Disciplines and Strategies.
    Indexed across 8 core worldwide quantitative and discretionary pillars.
    """

    def __init__(self):
        self.disciplines = {
            "SCALPING_AND_ORDER_FLOW": {
                "name": "High-Frequency Scalping & Order Flow",
                "principles": [
                    "Sub-second tick-level monitoring of depth and volume delta.",
                    "Exploitation of micro-spreads with instantaneous exit triggers.",
                    "Strict avoidance of overnight exposure."
                ],
                "primary_indicators": ["Tick Velocity", "Volume Delta", "Micro VWAP"]
            },
            "MOMENTUM_BREAKOUT": {
                "name": "Momentum & Volatility Breakout",
                "principles": [
                    "Expansion through multi-period resistance or Previous Day High (PDH).",
                    "Volume surge threshold: Minimum 1.5x of 20-period moving average.",
                    "Asymmetric profit expansion targeting 2.0x to 3.0x ATR."
                ],
                "primary_indicators": ["SuperTrend (10,3)", "EMA 9/21/50", "ADX Trend Strength"]
            },
            "SMART_MONEY_CONCEPTS_SMC": {
                "name": "Institutional Smart Money Concepts (SMC)",
                "principles": [
                    "Identification of Fair Value Gaps (FVG) and institutional liquidity imbalances.",
                    "Liquidity sweeps: Exploiting retail stop-loss clusters before true directional rallies.",
                    "Break of Structure (BOS) and Change of Character (CHoCH) trend shifts."
                ],
                "primary_indicators": ["FVG Imbalances", "Order Blocks", "Liquidity Sweep Wicks"]
            },
            "MEAN_REVERSION_AND_STAT_ARB": {
                "name": "Statistical Arbitrage & Mean Reversion",
                "principles": [
                    "Price extremes beyond 2.0 standard deviations from VWAP or 20 SMA.",
                    "RSI divergence at extreme overbought (>75) or oversold (<25) boundaries.",
                    "Pairs trading and cross-asset mean reversion (e.g., Gold/Silver ratio)."
                ],
                "primary_indicators": ["Bollinger Bands (20, 2.0)", "RSI Divergence", "Z-Score"]
            },
            "OPTIONS_GREEKS_AND_DERIVATIVES": {
                "name": "Options Trading, Greeks & Volatility Surface",
                "principles": [
                    "Delta directionality combined with positive Gamma acceleration.",
                    "Theta decay management: Avoiding long out-of-the-money options near expiry.",
                    "Option Chain Put-Call Ratio (PCR): Institutional floor when PCR > 1.2."
                ],
                "primary_indicators": ["Put-Call Ratio (PCR)", "India VIX", "Open Interest Buildup"]
            },
            "MACRO_AND_COMMODITY_CYCLES": {
                "name": "Global Macro & Commodity Supercycles",
                "principles": [
                    "Central Bank interest rate cycles and monetary liquidity policy.",
                    "LME metals & Chinese infrastructure stimulus driving steel and mining stocks.",
                    "OPEC quotas and geopolitical supply chokepoint premiums driving crude oil."
                ],
                "primary_indicators": ["LME Metal Index", "DXY Dollar Index", "Brent Crude"]
            },
            "ASYMMETRIC_LOSS_SUPPRESSION": {
                "name": "FinPos Asymmetric Loss Suppression",
                "principles": [
                    "Sever adverse price drops at -0.40% to -0.50% in fractions of a second.",
                    "Never allow green trades to retrace into red losses via tiered profit floors.",
                    "Portfolio Kelly Criterion position sizing strictly capping trade risk to 1.5%."
                ],
                "primary_indicators": ["Tick Drawdown Monitor", "Trailing ATR Stop", "Kelly Allocation"]
            }
        }

    def get_all_disciplines(self) -> Dict[str, Any]:
        return self.disciplines

    def query_strategy_context(self, strategy_type: str) -> Dict[str, Any]:
        return self.disciplines.get(strategy_type, self.disciplines["MOMENTUM_BREAKOUT"])

universal_trading_knowledge = UniversalTradingKnowledgeBase()
