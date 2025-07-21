from typing import TypedDict
from datetime import datetime
from dataclasses import dataclass

@dataclass
class Option:
    uly_currency: str
    expiry: datetime.date
    strike: int
    option_type: str


class OptionData(TypedDict):
    exchange: str
    uly_currency: str
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

    async def subscribe_bid_ask(self, instruments: list[str]):
        """Subscribe to bid/ask updates for a list of instruments."""
        pass

    def to_option(self, instrument: str) -> Option:
        """Convert instrument string to Option."""
        pass
