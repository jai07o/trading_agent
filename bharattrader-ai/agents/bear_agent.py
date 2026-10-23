from typing import Dict, Any, List

class BearAnalystAgent:
    """
    Bear Thesis & Risk Analyst for Indian Markets.
    Identifies resistance rejection, exhaustion, overbought hazards, and downside hazards.
    """

    def evaluate(self, tech_report: Dict[str, Any], india_vix: float = 13.5) -> Dict[str, Any]:
        indicators = tech_report.get("indicators", {})
        price = tech_report.get("current_price", 0.0)
        rsi = indicators.get("rsi", 50.0)
        
        bear_confidence = 50.0
        warnings: List[str] = []

        # 1. Overbought exhaustion
        if rsi >= 72.0:
            bear_confidence += 25.0
            warnings.append(f"RSI extreme overbought at {rsi:.1f} — high likelihood of sharp profit booking")
        elif rsi >= 65.0:
            bear_confidence += 10.0
            warnings.append(f"RSI elevated at {rsi:.1f} — upside room narrowing")

        # 2. VWAP rejection
        if price < indicators.get("vwap", 0.0):
            bear_confidence += 20.0
            warnings.append("Price struggling below VWAP — institutional supply present")

        # 3. India VIX spike (> 16 indicates volatile wild swings)
        if india_vix > 16.0:
            bear_confidence += 15.0
            warnings.append(f"India VIX elevated at {india_vix:.2f} — sudden volatility risk")
        elif india_vix < 11.0:
            bear_confidence += 5.0
            warnings.append("India VIX very low — option premiums compressed, sudden spikes likely")

        # 4. Supertrend
        if indicators.get("supertrend") == "BEARISH":
            bear_confidence += 15.0
            warnings.append("SuperTrend remains red overhead resistance")

        bear_confidence = min(98.0, max(5.0, bear_confidence))

        return {
            "agent": "Bear Analyst",
            "stance": "BEARISH" if bear_confidence >= 60 else "NEUTRAL",
            "risk_level": "HIGH" if bear_confidence >= 70 else ("MEDIUM" if bear_confidence >= 45 else "LOW"),
            "confidence": round(bear_confidence, 1),
            "warnings": warnings,
            "downside_target": round(price * 0.985, 2)
        }

bear_agent = BearAnalystAgent()
