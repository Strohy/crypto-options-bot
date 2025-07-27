from options.aggregator import Aggregator
import asyncio
from dataclasses import dataclass
from options.base_exchange import Option, OptionQuoteUpdate
from typing import Optional


@dataclass
class Quote:
    exchange: Optional[str] = None
    price: Optional[float] = None


@dataclass
class BestQuote:
    highest_bid: Quote
    lowest_ask: Quote

    def update(self, new_quote: OptionQuoteUpdate):
        if new_quote.bid is not None:
            if self.highest_bid is None or new_quote.bid > self.highest_bid.price:
                self.highest_bid = Quote(
                    exchange=new_quote.exchange, price=new_quote.bid
                )

        if new_quote.ask is not None:
            if self.lowest_ask is None or new_quote.ask < self.lowest_ask.price:
                self.lowest_ask = Quote(
                    exchange=new_quote.exchange, price=new_quote.ask
                )

        # If conditions are satisfied, execute trading logic


class OptionQuotes:
    def __init__(self, options: list[Option]):
        self.quotes = {
            option: BestQuote(highest_bid=None, lowest_ask=None) for option in options
        }

    def update(self, new_quote: OptionQuoteUpdate):
        # print(new_quote.exchange)  # Remove after debugging
        self.quotes[new_quote.option].update(new_quote)


async def main():
    EXCHANGE_LIST = ["Deribit", "Okx"]

    aggregator = Aggregator(EXCHANGE_LIST)

    await aggregator.connect()

    common_options = await aggregator.common_options()

    quotes = OptionQuotes(common_options[:1])

    await aggregator.subscribe_bid_ask(common_options[:1], quotes.update)


if __name__ == "__main__":
    asyncio.run(main())
