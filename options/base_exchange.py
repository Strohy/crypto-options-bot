from typing import TypedDict
import pandas as pd


class OptionData(TypedDict):
    exchange: str
    symbol: str
    option_type: str
    strike: any
    expiry: str
    bid: any
    ask: any
    instrument_name: str
    timestamp: str


class Exchange:
    def connect(self):
        """Connect to the exchange WebSocket or REST."""
        pass

    async def list_options(self, currency: str = "ETH"):
        """Subscribe to ETH options bid/ask data."""
        pass

    async def get_bid_ask(self, instrument_id: str) -> dict:
        """Return latest bid/ask for a given option."""
        pass

    async def subscribe_bid_ask(self, instruments: list[str], database: pd.DataFrame):
        """Subscribe to bid/ask updates for a list of instruments."""
        pass
