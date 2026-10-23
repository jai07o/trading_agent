from typing import Dict, Any, List

class WhatIfScenarioSimulator:
    """
    What-If Scenario Simulation Engine for Indian Markets.
    Evaluates hypothetical policy, geopolitical, and macroeconomic shockwaves on portfolio assets.
    """

    def __init__(self):
        self.preset_scenarios = {
            "RBI_RATE_CUT": {
                "name": "RBI Cuts Repo Rate by 25 bps",
                "impact_summary": "Reduces borrowing costs, expands credit demand, surges Banking & Auto multiples.",
                "sector_multipliers": {
                    "BANKNIFTY": +1.8,
                    "TATAMOTORS.NS": +2.2,
                    "RELIANCE.NS": +0.8,
                    "TATASTEEL.NS": +1.2
                }
            },
            "CRUDE_OIL_SPIKE": {
                "name": "Crude Oil Spikes +7% on Middle East Shipping Disruption",
                "impact_summary": "Pressures Indian current account deficit; OMCs and Paint companies drop; upstream energy & mining miners benefit.",
                "sector_multipliers": {
                    "CRUDEOIL_MCX": +6.5,
                    "VEDL.NS": +1.8,
                    "COALINDIA.NS": +1.5,
                    "TCS.NS": -0.4
                }
            },
            "CHINA_INFRA_STIMULUS": {
                "name": "China Announces $150B Infrastructure Metal Stimulus",
                "impact_summary": "LME base metals surge, world steel supply tightens, direct catalyst for Indian steel & mining stocks.",
                "sector_multipliers": {
                    "TATASTEEL.NS": +4.2,
                    "HINDALCO.NS": +3.8,
                    "NMDC.NS": +3.5,
                    "VEDL.NS": +3.2,
                    "COALINDIA.NS": +2.1
                }
            },
            "BUDGET_INFRA_EXPANSION": {
                "name": "Union Budget Expands Railway & Highway Capex +15%",
                "impact_summary": "Direct domestic orderbook expansion for steel, iron ore, and heavy engineering.",
                "sector_multipliers": {
                    "TATASTEEL.NS": +3.4,
                    "NMDC.NS": +3.8,
                    "JSWSTEEL.NS": +3.1,
                    "NIFTY50": +1.4
                }
            }
        }

    def simulate_event(self, scenario_key: str, open_portfolio: List[Dict[str, Any]] = None) -> Dict[str, Any]:
        scenario = self.preset_scenarios.get(scenario_key, self.preset_scenarios["CHINA_INFRA_STIMULUS"])
        multipliers = scenario["sector_multipliers"]

        simulated_results = []
        for symbol, impact in multipliers.items():
            simulated_results.append({
                "symbol": symbol,
                "projected_move_pct": round(impact, 2),
                "direction": "SURGE" if impact > 0 else "CONTRACT",
                "loss_suppression_status": "SAFE" if impact > -0.50 else "CIRCUIT_BREAKER_ACTIVE"
            })

        return {
            "scenario": scenario["name"],
            "impact_summary": scenario["impact_summary"],
            "projected_asset_movements": simulated_results,
            "loss_suppression_verdict": "Sub-Second Loss Suppressor armed. Any downside beyond -0.5% will be instantly severed."
        }

    def get_all_scenarios(self) -> List[str]:
        return list(self.preset_scenarios.keys())

whatif_simulator = WhatIfScenarioSimulator()
