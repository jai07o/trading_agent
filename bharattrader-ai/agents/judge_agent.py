from typing import Dict, Any, List
from agents.trend_agent import trend_agent
from agents.bull_agent import bull_agent
from agents.bear_agent import bear_agent
from agents.sentiment_agent import sentiment_agent
from core.self_learning import self_learning_engine
from core.cross_market_graph import cross_market_graph
from core.model_disagreement import model_disagreement_engine

class QuantJudgeAgent:
    """
    Project Apex: Chief Quant Judge Agent.
    Aggregates Technicals, Bull Case, Bear Case, Market Sentiment,
    Cross-Market Macro Relationships, and Model Disagreement / Uncertainty.
    
    Uses dynamic Bayesian weights from Self-Learning, stress-tests against
    cross-market headwinds, and enforces a mandatory ABSTAIN when independent
    models conflict.
    """

    def adjudicate(self, symbol: str, df) -> Dict[str, Any]:
        # 1. Gather all sub-agent intelligence
        tech = trend_agent.analyze_ticker(symbol, df)
        sentiment = sentiment_agent.get_market_sentiment(symbol)
        bull = bull_agent.evaluate(tech, option_pcr=sentiment.get("pcr", 1.0))
        bear = bear_agent.evaluate(tech, india_vix=sentiment.get("india_vix", 13.5))

        # 2. Multi-source weighted fusion with self-learned weights
        weights = self_learning_engine.agent_weights
        w_tech = weights.get("technicals", 0.40)
        w_bull = weights.get("bull_analyst", 0.25)
        w_bear = weights.get("bear_analyst", 0.20)
        w_sent = weights.get("sentiment", 0.15)

        tech_score = tech.get("score", 50.0)
        bull_score = bull.get("confidence", 50.0)
        bear_penalty = bear.get("confidence", 50.0)
        sent_score = sentiment.get("sentiment_score", 50.0)

        # Cross-market macro context
        macro_signal = cross_market_graph.get_symbol_macro_headwind(symbol)
        macro_impact = macro_signal.get("impact", 0)

        fused_score = (
            (tech_score * w_tech) +
            (bull_score * w_bull) +
            ((100.0 - bear_penalty) * w_bear) +
            (sent_score * w_sent) +
            macro_impact
        )
        fused_score = min(99.0, max(1.0, fused_score))

        price = tech.get("current_price", 0.0)
        atr = tech.get("indicators", {}).get("atr", price * 0.01)

        # 3. Model Disagreement & Epistemic Uncertainty Audit
        disagreement = model_disagreement_engine.evaluate_model_disagreement(
            symbol=symbol,
            trend_score=tech_score,
            bull_score=bull_score,
            bear_score=bear_penalty,
            sentiment_score=sent_score,
            swarm_buy_pct=bull_score
        )

        # 4. Decision thresholding with Uncertainty Gating
        if not disagreement["trade_permitted"]:
            # Hard abstain: independent models in high conflict or data stale
            action = "HOLD"
            confidence = round(100.0 - disagreement["uncertainty_pct"], 1)
            target_1 = price
            target_2 = price
            stop_loss = price
            summary = f"ABSTAIN (Uncertainty {disagreement['uncertainty_pct']}%): {disagreement['verdict_rationale']}"
        elif fused_score >= 68.0:
            action = "BUY"
            confidence = fused_score
            target_1 = round(price + (1.2 * atr), 2)
            target_2 = round(price + (2.5 * atr), 2)
            stop_loss = round(price - (0.5 * atr), 2) # Tight sub-second loss boundary
            summary = f"Strong Long Signal on {symbol}: Macro {macro_signal['alignment']}, model consensus verified."
        elif fused_score <= 32.0:
            action = "SELL"
            confidence = 100.0 - fused_score
            target_1 = round(price - (1.2 * atr), 2)
            target_2 = round(price - (2.5 * atr), 2)
            stop_loss = round(price + (0.5 * atr), 2)
            summary = f"Bearish Pressure on {symbol}: Bear thesis dominates, breaking below support."
        else:
            action = "HOLD"
            confidence = round(100.0 - abs(fused_score - 50.0) * 2, 1)
            target_1 = price
            target_2 = price
            stop_loss = price
            summary = f"Neutral / Indecisive on {symbol}: Risk-reward insufficient. Capital safely preserved."

        return {
            "symbol": symbol,
            "action": action,
            "fused_score": round(fused_score, 1),
            "confidence": round(confidence, 1),
            "current_price": price,
            "entry_price": price,
            "target_1": target_1,
            "target_2": target_2,
            "stop_loss": stop_loss,
            "chart_patterns": tech.get("patterns", []),
            "active_learned_weights": weights,
            "macro_alignment": macro_signal,
            "model_disagreement": disagreement,
            "permitted_size_factor": disagreement.get("permitted_size_factor", 1.0),
            "risk_reward_ratio": "2.4 : 1" if action != "HOLD" else "N/A",
            "summary": summary,
            "sub_agent_reports": {
                "technicals": tech,
                "bull_analyst": bull,
                "bear_analyst": bear,
                "sentiment": sentiment
            }
        }

judge_agent = QuantJudgeAgent()
