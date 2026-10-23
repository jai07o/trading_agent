from abc import ABC, abstractmethod
from typing import Dict, Any, List

class BaseBroker(ABC):
    """Abstract Base Class for Indian Stock Brokers."""

    @abstractmethod
    def get_account_summary(self) -> Dict[str, Any]:
        """Returns cash, portfolio value, P&L in INR."""
        pass

    @abstractmethod
    def get_positions(self) -> List[Dict[str, Any]]:
        """Returns list of open active positions."""
        pass

    @abstractmethod
    def place_order(self, symbol: str, side: str, quantity: int, price: float, stop_loss: float = None, target: float = None) -> Dict[str, Any]:
        """Places a new order."""
        pass

    @abstractmethod
    def close_position(self, symbol: str, current_price: float, reason: str = "MANUAL") -> Dict[str, Any]:
        """Closes an open position immediately."""
        pass

    @abstractmethod
    def get_live_quote(self, symbol: str) -> float:
        """Fetches the latest live market price."""
        pass
