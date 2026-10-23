import math
import statistics
from typing import Dict, Any, List, Optional

class ModelDisagreementEngine:
    """
    Project Apex: Model Disagreement & Uncertainty Engine.
    Evaluates disagreement and epistemic variance across independent sub-models:
    1. Trend & Technical Agent
    2. Bull Analyst Agent
    3. Bear Analyst Agent
    4. Sentiment / Options Derivative Agent
    5. 20-Agent Monte Carlo Swarm

    Core Rule:
    When independent models disagree materially, uncertainty increases.
    The agent dynamically de-risks by slashing position size or issuing a
    mandatory ABSTAIN (NO_TRADE) verdict to prevent capital destruction.
    """

    def __init__(self):
        # Thresholds for decision gating
        self.consensus_threshold = 0.35   # Low disagreement: Full execution
        self.caution_threshold = 0.65     # Moderate disagreement: 50% de-risking
        # > 0.65 is High Disagreement: ABSTAIN / NO_TRADE

    def evaluate_model_disagreement(
        self,
        symbol: str,
        trend_score: float,
        bull_score: float,
        bear_score: float,
        sentiment_score: float,
        swarm_buy_pct: float,
        data_latency_ms: float = 42.0
    ) -> Dict[str, Any]:
        """
        Quantifies disagreement index, epistemic uncertainty, and assigns
        a deterministic risk action.
        """
        # Normalize all signals into a 0 - 100 bullish scale
        # bear_score is bearishness (0-100), so its bullish equivalent is (100 - bear_score)
        bear_bullish_equiv = 100.0 - bear_score
        
        signals = [
            ("Trend_SuperTrend", float(trend_score)),
            ("Bull_Analyst", float(bull_score)),
            ("Bear_Inverted", float(bear_bullish_equiv)),
            ("Sentiment_PCR", float(sentiment_score)),
            ("Swarm_Consensus", float(swarm_buy_pct))
        ]

        scores = [s[1] for s in signals]
        mean_score = statistics.mean(scores)
        
        if len(scores) > 1:
            stdev = statistics.stdev(scores)
        else:
            stdev = 0.0

        # Maximum theoretical std dev on a 0-100 scale is 50.0 (e.g. split between 0 and 100)
        raw_disagreement_index = min(1.0, stdev / 50.0)

        # Polarization metric: measures if models are split on opposite sides of 50
        bullish_count = sum(1 for s in scores if s >= 55)
        bearish_count = sum(1 for s in scores if s <= 45)
        is_polarized = (bullish_count >= 2 and bearish_count >= 2)

        if is_polarized:
            # Polarized conflict sharply amplifies epistemic uncertainty
            disagreement_index = min(1.0, raw_disagreement_index * 1.35)
        else:
            disagreement_index = raw_disagreement_index

        uncertainty_pct = round(disagreement_index * 100.0, 1)

        # Policy Enforcement Decision
        if data_latency_ms > 2500.0:
            policy_action = "ABSTAIN_STALE_DATA"
            permitted_size_factor = 0.0
            verdict_rationale = f"Feed latency {data_latency_ms:.0f}ms exceeds safety limit (2500ms). Trading halted."
            trade_permitted = False
        elif disagreement_index > self.caution_threshold:
            policy_action = "MANDATORY_ABSTAIN"
            permitted_size_factor = 0.0
            verdict_rationale = (
                f"Severe model disagreement (Index: {disagreement_index:.2f}, Uncertainty: {uncertainty_pct}%). "
                f"Models in direct opposition (Bullish models: {bullish_count}, Bearish models: {bearish_count}). "
                "Project Apex rule enforced: Do not trade into high epistemic uncertainty."
            )
            trade_permitted = False
        elif disagreement_index > self.consensus_threshold:
            policy_action = "DERISK_HALF_SIZE"
            permitted_size_factor = 0.50
            verdict_rationale = (
                f"Moderate model divergence (Index: {disagreement_index:.2f}). "
                "Confidence acceptable but not unanimous. Position size de-risked by 50%."
            )
            trade_permitted = True
        else:
            policy_action = "FULL_CONSENSUS"
            permitted_size_factor = 1.0
            verdict_rationale = (
                f"High model alignment (Index: {disagreement_index:.2f}, Uncertainty: {uncertainty_pct}%). "
                "Sub-agents in unified agreement. Full risk budget permitted."
            )
            trade_permitted = True

        return {
            "symbol": symbol,
            "mean_opinion_score": round(mean_score, 1),
            "dispersion_stdev": round(stdev, 2),
            "disagreement_index": round(disagreement_index, 3),
            "uncertainty_pct": uncertainty_pct,
            "is_polarized": is_polarized,
            "data_latency_ms": data_latency_ms,
            "policy_action": policy_action,
            "permitted_size_factor": permitted_size_factor,
            "trade_permitted": trade_permitted,
            "verdict_rationale": verdict_rationale,
            "model_breakdown": {name: score for name, score in signals}
        }

model_disagreement_engine = ModelDisagreementEngine()
