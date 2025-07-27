from datetime import datetime
from dataclasses import dataclass
from typing import Optional


@dataclass(frozen=True, eq=True)
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
    option: Option
    bid: Optional[float]
    ask: Optional[float]


class Exchange:
    async def connect(self):
        """Connect to the exchange WebSocket or REST."""
        pass

    async def list_options(self, currency: str) -> list[Option]:
        """Subscribe to ETH options bid/ask data."""
        pass

    async def get_bid_ask(self, instrument: str) -> OptionQuoteUpdate:
        """Return latest bid/ask for a given option."""
        pass

    async def subscribe_bid_ask(self, instruments: list[Option], function):
        """Subscribe to bid/ask updates for a list of instruments."""
        pass

    def from_option(self, option: Option) -> str:
        """Convert Option type to instrument string."""

    def to_option(self, instrument: str) -> Option:
        """Convert instrument string to Option type."""
        pass
