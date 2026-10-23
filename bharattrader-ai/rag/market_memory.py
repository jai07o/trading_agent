from typing import Dict, Any, List

class IndianMarketRAGMemory:
    """
    RAG (Retrieval-Augmented Generation) Market Memory for BharatTrader AI.
    Indexes historical Indian market knowledge, quarterly earnings, mining policies, and RBI circulars.
    """

    def __init__(self):
        self.knowledge_base = [
            {
                "topic": "Mining Royalty & MMDR Act",
                "content": "Mines and Minerals (Development and Regulation) Act encourages commercial auction. Coal India and NMDC maintain strong cost advantages."
            },
            {
                "topic": "Indian Steel Export Duty & Anti-Dumping",
                "content": "Directorate General of Trade Remedies (DGTR) reviews anti-dumping duties on hot-rolled and cold-rolled steel coils, guarding domestic steel mill margins."
            },
            {
                "topic": "RBI Monetary Policy Committee Framework",
                "content": "Inflation target band 4% (+/- 2%). Rate pause and liquidity management via standing deposit facility (SDF) provides macroeconomic stability."
            },
            {
                "topic": "Option Chain Put-Call Ratio (PCR) Rule",
                "content": "PCR > 1.25 indicates extreme bullish floor (put writers dominant). PCR < 0.75 indicates extreme bearish overhead ceiling."
            }
        ]

    def query_context(self, query: str) -> List[Dict[str, str]]:
        """Retrieves relevant semantic knowledge chunks based on query keywords."""
        query_lower = query.lower()
        results = []
        for doc in self.knowledge_base:
            if any(term in doc["content"].lower() or term in doc["topic"].lower() for term in query_lower.split()):
                results.append(doc)
        if not results:
            results = self.knowledge_base[:2]
        return results

rag_memory = IndianMarketRAGMemory()
