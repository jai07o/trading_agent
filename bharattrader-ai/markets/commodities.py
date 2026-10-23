import random
from typing import Dict, Any, List

class MCXCommoditiesAnalyst:
    """
    Dedicated Multi Commodity Exchange of India (MCX) Analyst.
    Tracks Gold, Silver, Crude Oil, Copper, and Natural Gas in Indian Rupees.
    """

    def __init__(self):
        self.commodity_quotes = {
            "GOLD_MCX": {
                "name": "MCX Gold (10g)",
                "price": 78450.0,
                "unit": "₹ / 10 grams",
                "lot_size": 1,
                "margin_pct": 11.0
            },
            "SILVER_MCX": {
                "name": "MCX Silver (1kg)",
                "price": 94820.0,
                "unit": "₹ / 1 kg",
                "lot_size": 1,
                "margin_pct": 12.5
            },
            "CRUDEOIL_MCX": {
                "name": "MCX Crude Oil",
                "price": 6140.0,
                "unit": "₹ / Barrel",
                "lot_size": 100,
                "margin_pct": 22.0
            },
            "COPPER_MCX": {
                "name": "MCX Copper",
                "price": 842.50,
                "unit": "₹ / kg",
                "lot_size": 2500,
                "margin_pct": 14.0
            },
            "NATGAS_MCX": {
                "name": "MCX Natural Gas",
                "price": 218.40,
                "unit": "₹ / mmBtu",
                "lot_size": 1250,
                "margin_pct": 25.0
            }
        }

    def analyze_commodity(self, symbol: str) -> Dict[str, Any]:
        info = self.commodity_quotes.get(symbol, {"name": symbol, "price": 5000.0, "unit": "₹", "lot_size": 1, "margin_pct": 15.0})
        price = info["price"]
        
        # Macro commodity drivers
        dxy_dollar_index = round(random.uniform(103.2, 105.8), 2)
        gold_silver_ratio = round(78450.0 / 948.20, 2) # approx 82.7
        opec_stance = "Production Quota Restraint Active"

        catalysts = []
        score = 50.0

        if symbol == "GOLD_MCX":
            score += 22.0
            catalysts.append("Central bank gold reserves accumulation continuing at multi-decade highs")
            catalysts.append(f"Geopolitical flight-to-safety hedging supporting floor above ₹77,500/10g")
        elif symbol == "SILVER_MCX":
            score += 26.0
            catalysts.append(f"Gold-Silver ratio at {gold_silver_ratio:.1f} indicates strong industrial silver undervaluation")
            catalysts.append("Photovoltaic solar cell production & electric vehicle wiring driving structural silver deficit")
        elif symbol == "CRUDEOIL_MCX":
            score += 12.0
            catalysts.append(f"OPEC+ compliance strict; {opec_stance}")
            catalysts.append("Middle East shipping route risk premium priced into Brent / MCX futures")
        elif symbol == "COPPER_MCX":
            score += 18.0
            catalysts.append("Global energy grid expansion and AI data center power infrastructure fueling copper demand")

        score = min(98.0, max(15.0, score))

        return {
            "symbol": symbol,
            "name": info["name"],
            "price": price,
            "unit": info["unit"],
            "lot_size": info["lot_size"],
            "margin_requirement_pct": info["margin_pct"],
            "commodity_score": round(score, 1),
            "stance": "BULLISH" if score >= 65 else ("BEARISH" if score <= 40 else "NEUTRAL"),
            "drivers": catalysts,
            "gold_silver_ratio": gold_silver_ratio
        }

    def get_all_commodities(self) -> List[Dict[str, Any]]:
        return [self.analyze_commodity(sym) for sym in self.commodity_quotes.keys()]

mcx_commodities_analyst = MCXCommoditiesAnalyst()
