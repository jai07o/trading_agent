import numpy as np
import pandas as pd
from typing import Dict, Any, List
from core.chart_patterns import chart_pattern_engine

class TrendTechnicalsAgent:
    """
    Technical & Quantitative Analysis Agent for Indian Market (NSE/BSE).
    Calculates SuperTrend, EMAs, RSI, VWAP, ATR, and runs Universal Chart & Candlestick Pattern Recognition.
    """

    def analyze_ticker(self, symbol: str, df: pd.DataFrame) -> Dict[str, Any]:
        """
        Analyzes OHLCV dataframe and returns structured technical signals + detected chart patterns.
        """
        if df is None or len(df) < 15:
            return {
                "symbol": symbol,
                "status": "INSUFFICIENT_DATA",
                "trend": "NEUTRAL",
                "score": 50.0,
                "indicators": {},
                "patterns": []
            }

        close = df['Close'].values
        high = df['High'].values
        low = df['Low'].values
        volume = df['Volume'].values if 'Volume' in df.columns else np.ones(len(close))

        current_price = float(close[-1])

        # 1. Exponential Moving Averages (9, 21, 50, 200)
        ema9 = float(pd.Series(close).ewm(span=9, adjust=False).mean().iloc[-1])
        ema21 = float(pd.Series(close).ewm(span=21, adjust=False).mean().iloc[-1])
        ema50 = float(pd.Series(close).ewm(span=50, adjust=False).mean().iloc[-1]) if len(close) >= 50 else ema21
        ema200 = float(pd.Series(close).ewm(span=200, adjust=False).mean().iloc[-1]) if len(close) >= 200 else ema50

        # 2. RSI (14)
        delta = pd.Series(close).diff()
        gain = delta.where(delta > 0, 0.0)
        loss = -delta.where(delta < 0, 0.0)
        avg_gain = gain.rolling(window=14, min_periods=14).mean().iloc[-1]
        avg_loss = loss.rolling(window=14, min_periods=14).mean().iloc[-1]
        if avg_loss == 0:
            rsi = 100.0
        else:
            rs = avg_gain / avg_loss
            rsi = float(100.0 - (100.0 / (1.0 + rs)))
        if np.isnan(rsi):
            rsi = 50.0

        # 3. ATR (Average True Range)
        tr1 = high - low
        tr2 = np.abs(high - np.roll(close, 1))
        tr3 = np.abs(low - np.roll(close, 1))
        tr = np.maximum(tr1, np.maximum(tr2, tr3))
        atr = float(pd.Series(tr).rolling(14).mean().iloc[-1])
        if np.isnan(atr) or atr <= 0:
            atr = float(current_price * 0.01)

        # 4. VWAP Approximation
        typical_price = (high + low + close) / 3.0
        cum_vp = np.cumsum(typical_price * volume)
        cum_v = np.cumsum(volume)
        vwap = float((cum_vp / np.where(cum_v == 0, 1, cum_v))[-1])

        # 5. SuperTrend (10, 3) approximation
        hl2 = (high[-1] + low[-1]) / 2.0
        upper_band = hl2 + (3.0 * atr)
        lower_band = hl2 - (3.0 * atr)
        supertrend_bullish = current_price > lower_band

        # 6. UNIVERSAL CHART & CANDLESTICK PATTERN RECOGNITION (Ups and Downs)
        detected_patterns = chart_pattern_engine.detect_patterns(df)

        # 7. Scoring & Trend Determination
        trend_score = 50.0
        bullish_factors = []
        bearish_factors = []

        if current_price > vwap:
            trend_score += 10.0
            bullish_factors.append(f"Price (₹{current_price:.2f}) trading above VWAP (₹{vwap:.2f})")
        else:
            trend_score -= 10.0
            bearish_factors.append(f"Price (₹{current_price:.2f}) below VWAP (₹{vwap:.2f})")

        if ema9 > ema21:
            trend_score += 12.0
            bullish_factors.append("EMA 9 crossed above EMA 21 (Short-term momentum positive)")
        else:
            trend_score -= 12.0
            bearish_factors.append("EMA 9 below EMA 21 (Short-term momentum negative)")

        if current_price > ema50:
            trend_score += 6.0
            bullish_factors.append("Above 50 EMA institutional trendline")
        else:
            trend_score -= 6.0

        if 40.0 <= rsi <= 65.0:
            trend_score += 6.0
            bullish_factors.append(f"RSI healthy at {rsi:.1f} (in sweet spot, not overbought)")
        elif rsi > 70.0:
            trend_score -= 10.0
            bearish_factors.append(f"RSI overbought at {rsi:.1f}")
        elif rsi < 30.0:
            trend_score += 5.0
            bullish_factors.append(f"RSI oversold at {rsi:.1f} (potential mean reversion)")

        if supertrend_bullish:
            trend_score += 8.0
            bullish_factors.append("SuperTrend is GREEN (Bullish trailing band active)")
        else:
            trend_score -= 8.0
            bearish_factors.append("SuperTrend is RED")

        # Pattern scoring impact
        for p in detected_patterns:
            if p["direction"] == "BULLISH_UP":
                trend_score += 12.0
                bullish_factors.append(f"PATTERN: {p['pattern']} (Target: ₹{p['projected_target']})")
            elif p["direction"] == "BEARISH_DOWN":
                trend_score -= 12.0
                bearish_factors.append(f"PATTERN: {p['pattern']} (Target: ₹{p['projected_target']})")

        trend_score = min(100.0, max(0.0, trend_score))

        if trend_score >= 65:
            overall_trend = "BULLISH"
        elif trend_score <= 35:
            overall_trend = "BEARISH"
        else:
            overall_trend = "RANGING_NEUTRAL"

        return {
            "symbol": symbol,
            "current_price": round(current_price, 2),
            "trend": overall_trend,
            "score": round(trend_score, 1),
            "indicators": {
                "rsi": round(rsi, 2),
                "vwap": round(vwap, 2),
                "ema9": round(ema9, 2),
                "ema21": round(ema21, 2),
                "ema50": round(ema50, 2),
                "ema200": round(ema200, 2),
                "atr": round(atr, 2),
                "supertrend": "BULLISH" if supertrend_bullish else "BEARISH"
            },
            "patterns": detected_patterns,
            "bullish_points": bullish_factors,
            "bearish_points": bearish_factors
        }

trend_agent = TrendTechnicalsAgent()
