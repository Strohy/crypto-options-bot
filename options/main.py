from options.deribit import Deribit
from options.okx import Okx
import asyncio
import datetime
from dataclasses import dataclass, field
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
                self.highest_bid = Quote(exchange=new_quote.exchange, price=new_quote.bid)

        if new_quote.ask is not None:
            if self.lowest_ask is None or new_quote.ask < self.lowest_ask.price:
                self.lowest_ask = Quote(exchange=new_quote.exchange, price=new_quote.ask)

        # If conditions are satisfied, execute trading logic


class OptionQuotes:
    def __init__(self, options: list[Option]):
        # self.options = {option.id(): option for option in options}
        self.quotes = {option.id(): BestQuote(highest_bid= None, lowest_ask=None) for option in options}

    def update(self, new_quote: OptionQuoteUpdate):
        self.quotes[new_quote.option_id].update(new_quote)


exchange_registry = {
    "Deribit": Deribit,
    "Okx": Okx,
}


class aggregator:
    def __init__(self, exchange_list: list[str]):
        # self.exchange_list = exchange_list
        self.exchanges = [
            exchange_registry[exchange_name] for exchange_name in exchange_list
        ]
        self.num_exchanges = len(self.exchanges)

    def connect(self):
        for exchange in self.exchanges:
            exchange.connect()

    def common_options(self):
        pass
        options = [ex.list_optins for ex in self.exchanges]


async def main():
    deribit = Deribit()
    await deribit.connect()

    okx = Okx()
    await okx.connect()

    options_deribit = await deribit.list_options("ETH")
    # print(f"Deribit options: {options_deribit[0]}")

    options_okx = await okx.list_options("ETH")
    # print(f"Okx options: {options_okx[0]}")

    options_common = [inst for inst in options_deribit if inst in options_okx]
    print(f"Common options: {options_common[0]}")

    quotes = OptionQuotes(options_common[:1])

    # await deribit.subscribe_bid_ask(
    #     options_common[:1],
    #     quotes.update,
    # )
    # await okx.subscribe_bid_ask(
    #     options_common[:1],
    #     quotes.update,
    # )

    task1 = asyncio.create_task(
        deribit.subscribe_bid_ask(options_common[:1], quotes.update)
    )
    task2 = asyncio.create_task(
        okx.subscribe_bid_ask(options_common[:1], quotes.update)
    )

    await asyncio.gather(
        task1,
        task2,
    )


if __name__ == "__main__":
    asyncio.run(main())
