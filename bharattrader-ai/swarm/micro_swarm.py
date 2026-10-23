import random
from typing import Dict, Any, List

class SwarmParticipant:
    def __init__(self, agent_id: int, persona: str, weight: float):
        self.agent_id = agent_id
        self.persona = persona
        self.weight = weight

    def evaluate_vote(self, signal_score: float, current_volatility: float) -> Dict[str, Any]:
        """Simulates how this specific market participant persona reacts."""
        bias = 0.0
        if "Institutional" in self.persona:
            bias = 0.08 if signal_score > 60 else -0.05
        elif "Scalper" in self.persona:
            bias = 0.12 if current_volatility > 1.2 else -0.08
        elif "Retail" in self.persona:
            bias = 0.15 if signal_score > 65 else -0.10
        elif "OptionWriter" in self.persona:
            bias = 0.05 if current_volatility < 1.4 else -0.15
        else: # Swing
            bias = 0.10 if signal_score > 55 else 0.0

        random_noise = random.uniform(-0.06, 0.06)
        vote_score = min(1.0, max(0.0, (signal_score / 100.0) + bias + random_noise))
        action = "BUY" if vote_score >= 0.60 else ("SELL" if vote_score <= 0.40 else "HOLD")
        
        return {
            "id": self.agent_id,
            "persona": self.persona,
            "vote": action,
            "conviction": round(vote_score * 100.0, 1)
        }

class TwentyAgentMicroSwarm:
    """
    20-Agent Micro Swarm Monte Carlo Simulator for Indian Order Books.
    Simulates convergence of market participants across 20 distinct profiles.
    """

    def __init__(self):
        self.participants = [
            SwarmParticipant(1, "DII Mutual Fund (Long Horizon)", 1.5),
            SwarmParticipant(2, "FII Quant Fund (Statistical Arbitrage)", 1.4),
            SwarmParticipant(3, "Prop Desk Index Scalper", 1.2),
            SwarmParticipant(4, "High Frequency Market Maker", 1.3),
            SwarmParticipant(5, "Nifty Option Put Writer (Floor Defense)", 1.4),
            SwarmParticipant(6, "Nifty Option Call Writer (Cap Defense)", 1.2),
            SwarmParticipant(7, "Retail Breakout Chaser", 0.9),
            SwarmParticipant(8, "Retail Social Momentum Trader", 0.8),
            SwarmParticipant(9, "Intraday VWAP Mean-Reversion Scalper", 1.1),
            SwarmParticipant(10, "SuperTrend Algorithmic Follower", 1.2),
            SwarmParticipant(11, "Sector Rotation Specialist", 1.1),
            SwarmParticipant(12, "FII Long-Short Hedge Fund", 1.3),
            SwarmParticipant(13, "Indian Family Office Value Accumulator", 1.2),
            SwarmParticipant(14, "Pari-Passu Arbitrage Desk", 1.0),
            SwarmParticipant(15, "Volatility Arbitrage Trader", 1.1),
            SwarmParticipant(16, "Intraday Volume Delta Scalper", 1.0),
            SwarmParticipant(17, "Closing Auction Imbalance Trader", 1.0),
            SwarmParticipant(18, "Gap-Fill Reversion Bot", 0.9),
            SwarmParticipant(19, "Gamma Squeeze Momentum Follower", 1.1),
            SwarmParticipant(20, "Long-Only Pension Fund Proxy", 1.2)
        ]

    def simulate(self, symbol: str, signal_score: float = 72.0) -> Dict[str, Any]:
        votes = []
        buy_weight = 0.0
        sell_weight = 0.0
        hold_weight = 0.0
        total_weight = 0.0

        for p in self.participants:
            res = p.evaluate_vote(signal_score, current_volatility=1.1)
            votes.append(res)
            
            if res["vote"] == "BUY":
                buy_weight += p.weight
            elif res["vote"] == "SELL":
                sell_weight += p.weight
            else:
                hold_weight += p.weight
            total_weight += p.weight

        buy_pct = (buy_weight / total_weight) * 100.0
        sell_pct = (sell_weight / total_weight) * 100.0
        hold_pct = (hold_weight / total_weight) * 100.0

        swarm_consensus = "BULLISH_CONVERGENCE" if buy_pct >= 60.0 else ("BEARISH_DIVERGENCE" if sell_pct >= 50.0 else "CHOPPY_DISPERSION")

        return {
            "symbol": symbol,
            "total_agents": 20,
            "total_micro_agents": 20,
            "swarm_consensus": swarm_consensus,
            "buy_pct": round(buy_pct, 1),
            "sell_pct": round(sell_pct, 1),
            "hold_pct": round(hold_pct, 1),
            "liquidity_conviction": "HIGH" if (buy_pct > 65 or sell_pct > 65) else "MODERATE",
            "participant_votes": votes[:6] # Top sample votes
        }

micro_swarm = TwentyAgentMicroSwarm()
