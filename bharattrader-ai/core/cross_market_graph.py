import math
import time
from typing import Dict, Any, List, Optional

class CrossMarketRelationshipGraph:
    """
    Project Apex: Cross-Market Relationship Graph.
    Models dynamic, non-stationary relationships among:
    - Domestic Equities: NIFTY 50, BANKNIFTY
    - Global Equities: S&P 500 (US), Nikkei 225
    - Currencies & Rates: USDINR, US 10-Year Treasury Yield, US Dollar Index (DXY)
    - Commodities & Energy: Brent Crude Oil, LME Copper, MCX Gold
    - Volatility Regimes: India VIX, CBOE VIX
    
    Identifies regime transitions and decorrelation anomalies where
    traditional statistical relationships break down.
    """

    def __init__(self):
        # Baseline canonical cross-market correlations (historical empirical anchors)
        self.canonical_correlations = {
            ("NIFTY50", "SPX500"): 0.68,
            ("NIFTY50", "USDINR"): -0.58,
            ("NIFTY50", "INDIA_VIX"): -0.74,
            ("NIFTY50", "BRENT_CRUDE"): -0.42,
            ("NIFTY50", "LME_COPPER"): 0.52,
            ("BANKNIFTY", "US10Y"): -0.45,
            ("GOLD", "US10Y"): -0.62,
            ("GOLD", "USDINR"): 0.38,
            ("COPPER", "BRENT_CRUDE"): 0.54,
            ("USDINR", "DXY"): 0.72
        }

        # Simulated dynamic rolling returns buffer for real-time tracking
        self.rolling_returns_window = {
            "NIFTY50": [+0.004, +0.008, -0.003, +0.005, +0.002, +0.007],
            "SPX500": [+0.006, +0.009, -0.002, +0.004, -0.001, +0.008],
            "USDINR": [-0.001, -0.002, +0.003, -0.001, +0.001, -0.002],
            "US10Y": [+0.002, -0.001, +0.004, -0.002, +0.001, +0.003],
            "DXY": [-0.002, -0.003, +0.005, -0.001, +0.002, -0.004],
            "BRENT_CRUDE": [-0.008, +0.004, +0.012, -0.005, +0.003, -0.006],
            "LME_COPPER": [+0.005, +0.011, -0.004, +0.008, +0.004, +0.009],
            "GOLD": [+0.003, +0.006, +0.002, +0.004, -0.001, +0.005],
            "INDIA_VIX": [-0.025, -0.040, +0.035, -0.018, -0.012, -0.030]
        }

    def _pearson_correlation(self, x: List[float], y: List[float]) -> float:
        """Calculates Pearson correlation between two series."""
        n = min(len(x), len(y))
        if n < 3:
            return 0.0
        
        x_sub = x[-n:]
        y_sub = y[-n:]
        mean_x = sum(x_sub) / n
        mean_y = sum(y_sub) / n
        
        cov = sum((x_sub[i] - mean_x) * (y_sub[i] - mean_y) for i in range(n))
        var_x = sum((x_sub[i] - mean_x) ** 2 for i in range(n))
        var_y = sum((y_sub[i] - mean_y) ** 2 for i in range(n))
        
        denominator = math.sqrt(var_x * var_y)
        if denominator == 0:
            return 0.0
        return max(-1.0, min(1.0, cov / denominator))

    def evaluate_cross_market_state(self) -> Dict[str, Any]:
        """
        Computes dynamic rolling cross-market matrix, identifies decorrelation
        shocks, and determines global macroeconomic regime.
        """
        current_correlations = {}
        anomalies = []

        for (asset_a, asset_b), canonical in self.canonical_correlations.items():
            series_a = self.rolling_returns_window.get(asset_a, [])
            series_b = self.rolling_returns_window.get(asset_b, [])
            
            if series_a and series_b:
                current_corr = round(self._pearson_correlation(series_a, series_b), 2)
            else:
                current_corr = canonical
                
            pair_key = f"{asset_a} <-> {asset_b}"
            current_correlations[pair_key] = {
                "current_correlation": current_corr,
                "historical_canonical": canonical,
                "divergence": round(current_corr - canonical, 2)
            }

            # Detect decorrelation breakdown
            # If canonical is positive and current becomes sharply negative, or vice versa
            if (canonical > 0.4 and current_corr < -0.1) or (canonical < -0.4 and current_corr > 0.1):
                anomalies.append({
                    "pair": pair_key,
                    "canonical": canonical,
                    "observed": current_corr,
                    "severity": "HIGH",
                    "description": f"Significant correlation decoupling detected between {asset_a} and {asset_b}."
                })

        # Classify current global macro regime
        vix_trend = self.rolling_returns_window["INDIA_VIX"][-1]
        spx_trend = self.rolling_returns_window["SPX500"][-1]
        brent_trend = self.rolling_returns_window["BRENT_CRUDE"][-1]
        copper_trend = self.rolling_returns_window["LME_COPPER"][-1]
        dxy_trend = self.rolling_returns_window["DXY"][-1]

        if spx_trend > 0 and vix_trend < 0 and copper_trend > 0:
            regime = "GLOBAL_RISK_ON"
            regime_summary = "Global equities advancing, volatility compressing, industrial metals in demand. Favorable tailwind."
            macro_exposure_multiplier = 1.0
        elif vix_trend > 0.02 or spx_trend < -0.01:
            regime = "GLOBAL_RISK_OFF"
            regime_summary = "Volatility spiking, equity risk premia widening. Defensive posture; enforce reduced sizing."
            macro_exposure_multiplier = 0.6
        elif brent_trend > 0.02 and dxy_trend > 0.003:
            regime = "IMPORT_COST_PRESSURE"
            regime_summary = "Crude rally and Dollar strengthening. Pressure on Indian CAD and import-heavy sectors."
            macro_exposure_multiplier = 0.75
        else:
            regime = "BALANCED_RANGE_BOUND"
            regime_summary = "Mixed global signals; cross-asset correlations operating near historical baselines."
            macro_exposure_multiplier = 0.85

        return {
            "regime": regime,
            "regime_summary": regime_summary,
            "macro_exposure_multiplier": macro_exposure_multiplier,
            "total_pairs_monitored": len(self.canonical_correlations),
            "correlation_matrix": current_correlations,
            "active_anomalies_count": len(anomalies),
            "anomalies": anomalies,
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S")
        }

    def get_symbol_macro_headwind(self, symbol: str) -> Dict[str, Any]:
        """Provides asset-specific cross-market headwinds or tailwinds."""
        state = self.evaluate_cross_market_state()
        regime = state["regime"]
        clean_sym = symbol.replace(".NS", "").upper()

        if clean_sym in ["TATASTEEL", "NMDC", "VEDL", "HINDALCO", "HINDZINC", "NATIONALUM"]:
            # Metals & Mining depends heavily on LME Copper, China demand, and DXY
            copper_trend = self.rolling_returns_window["LME_COPPER"][-1]
            if copper_trend > 0 and regime != "GLOBAL_RISK_OFF":
                return {"alignment": "FAVORABLE", "reason": "LME base metals surge provides sector support", "impact": +10}
            elif regime == "GLOBAL_RISK_OFF":
                return {"alignment": "UNFAVORABLE", "reason": "Global cyclical metal contraction during risk-off", "impact": -15}
        
        elif clean_sym in ["HDFCBANK", "ICICIBANK", "SBIN", "BANKNIFTY"]:
            # Banking depends on US10Y and domestic liquidity
            if regime == "GLOBAL_RISK_ON":
                return {"alignment": "FAVORABLE", "reason": "Institutional equity inflows supporting banking liquidity", "impact": +8}
            elif state["regime"] == "IMPORT_COST_PRESSURE":
                return {"alignment": "NEUTRAL", "reason": "Inflation stickiness limits RBI easing speed", "impact": -5}

        return {"alignment": "NEUTRAL", "reason": "Standard macro correlation baseline", "impact": 0}

cross_market_graph = CrossMarketRelationshipGraph()
