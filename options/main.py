from options.deribit import Deribit
from options.okx import Okx
import asyncio
import datetime
from dataclasses import dataclass
from options.base_exchange import Option, OptionQuoteUpdate


@dataclass
class Quote:
    exchange: str
    price: float


@dataclass
class BestQuote:
    highest_bid: Quote
    lowest_ask: Quote


class OptionQuotes:
    def __init__(self, options: list[Option]):
        # self.options = {}
        # for option in options:
        #     self.options[repr(option)] = option
        self.quotes = {}
        for option in options:
            self.quotes[option.id()] = BestQuote(highest_bid=None, lowest_ask=None)

    def update(self, new_quote: OptionQuoteUpdate):
        if (
            self.quotes[new_quote.option_id].highest_bid is None
            or new_quote.bid > self.quotes[new_quote.option_id].highest_bid.price
        ):
            # self.quotes[new_quote.option_id].highest_bid.price = new_quote.bid
            # self.quotes[new_quote.option_id].highest_bid.exchange = new_quote.exchange

            self.quotes[new_quote.option_id].highest_bid = Quote(
                exchange=new_quote.exchange, price=new_quote.bid
            )

            print("updated bid")

        if (
            self.quotes[new_quote.option_id].lowest_ask is None
            or new_quote.ask < self.quotes[new_quote.option_id].lowest_ask.price
        ):
            # self.quotes[new_quote.option_id].lowest_ask.price = new_quote.ask
            # self.quotes[new_quote.option_id].lowest_ask.exchange = new_quote.exchange

            self.quotes[new_quote.option_id].lowest_ask = Quote(
                exchange=new_quote.exchange, price=new_quote.ask
            )

            print("updated ask")

        print("Life goes")

        # If conditions are satisfied, execute trading logic


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

    await deribit.subscribe_bid_ask(
        [deribit.from_option(option) for option in options_common[:1]],
        quotes.update,
    )
    # okx.subscribe_bid_ask(list(map(okx.from_option, options_common)))


if __name__ == "__main__":
    asyncio.run(main())