from typing import Dict, Any, List

class BullAnalystAgent:
    """
    Bull Thesis Analyst for Indian Markets.
    Identifies momentum, breakout confirmation, institutional accumulation, and reward-to-risk.
    """

    def evaluate(self, tech_report: Dict[str, Any], option_pcr: float = 1.15) -> Dict[str, Any]:
        indicators = tech_report.get("indicators", {})
        price = tech_report.get("current_price", 0.0)
        atr = indicators.get("atr", price * 0.01)
        
        bull_confidence = 50.0
        reasons: List[str] = []

        # 1. Price above key levels
        if price > indicators.get("vwap", 0.0):
            bull_confidence += 15.0
            reasons.append("Intraday buyers in control above VWAP benchmark")

        if indicators.get("ema9", 0.0) > indicators.get("ema21", 0.0):
            bull_confidence += 15.0
            reasons.append("Short-term momentum acceleration (9 EMA > 21 EMA)")

        # 2. Option chain Put-Call Ratio (PCR > 1 indicates bullish support)
        if option_pcr > 1.05:
            bull_confidence += 12.0
            reasons.append(f"Derivative sentiment strongly bullish (PCR = {option_pcr:.2f})")
        elif option_pcr >= 0.95:
            bull_confidence += 5.0
            reasons.append(f"Derivative sentiment neutral-positive (PCR = {option_pcr:.2f})")

        # 3. Supertrend
        if indicators.get("supertrend") == "BULLISH":
            bull_confidence += 10.0
            reasons.append("SuperTrend confirms green upward channel")

        # 4. Target projection (1.5x and 3.0x ATR)
        target1 = price + (1.2 * atr)
        target2 = price + (2.5 * atr)
        stop_loss = price - (0.6 * atr)

        bull_confidence = min(98.0, max(5.0, bull_confidence))

        return {
            "agent": "Bull Analyst",
            "stance": "BULLISH" if bull_confidence >= 60 else "NEUTRAL",
            "confidence": round(bull_confidence, 1),
            "suggested_entry": round(price, 2),
            "target_1": round(target1, 2),
            "target_2": round(target2, 2),
            "stop_loss": round(stop_loss, 2),
            "reasons": reasons
        }

bull_agent = BullAnalystAgent()
