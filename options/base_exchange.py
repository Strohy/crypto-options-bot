from datetime import datetime
from dataclasses import dataclass


@dataclass
class Option:
    uly_currency: str
    expiry: datetime.date
    strike: int
    option_type: str

    def id(self) -> str:
        return f"{self.uly_currency}-{self.expiry}-{self.strike}-{self.option_type}"


@dataclass
class OptionQuoteUpdate:
    exchange: str
    option_id: str
    bid: float
    ask: float


class Exchange:
    def connect(self):
        """Connect to the exchange WebSocket or REST."""
        pass

    async def list_options(self, currency: str = "ETH") -> list[Option]:
        """Subscribe to ETH options bid/ask data."""
        pass

    async def get_bid_ask(self, instrument_id: str) -> OptionQuoteUpdate:
        """Return latest bid/ask for a given option."""
        pass

    async def subscribe_bid_ask(self, instruments: list[str]):
        """Subscribe to bid/ask updates for a list of instruments."""
        pass

    def from_option(self, option: Option) -> str:
        """Convert Option type to instrument string."""

    def to_option(self, instrument: str) -> Option:
        """Convert instrument string to Option type."""
        pass
