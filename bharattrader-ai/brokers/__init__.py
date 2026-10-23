from brokers.base_broker import BaseBroker
from brokers.paper_broker import paper_broker
from brokers.smartapi_broker import smartapi_broker
from config.settings import settings

def get_active_broker() -> BaseBroker:
    """Returns Live Broker if configured, otherwise Paper Broker."""
    if settings.TRADING_MODE == "LIVE" and smartapi_broker.is_connected:
        return smartapi_broker
    return paper_broker

__all__ = ["BaseBroker", "paper_broker", "smartapi_broker", "get_active_broker"]
