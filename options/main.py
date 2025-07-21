from options.deribit import Deribit
from options.okx import Okx
import asyncio
from datetime import datetime
from dataclasses import dataclass
from options.base_exchange import Option, OptionData


@dataclass
class Quote:
    exchange: str
    price: float


@dataclass
class OptionQuote:
    option: Option
    highest_bid: Quote
    lowest_ask: Quote

    def update(self, bid: Quote, ask: Quote):
        if bid.price > self.highest_bid.price or self.highest_bid is None:
            self.highest_bid = bid
        if ask.price < self.lowest_ask.price or self.lowest_ask is None:
            self.lowest_ask = ask

        # If conditions are satisfied, execute trading logic


async def main():
    deribit = Deribit()
    await deribit.connect()

    okx = Okx()
    await okx.connect()

    options_deribit = await deribit.list_options()
    options_deribit = [deribit.to_option(inst) for inst in options_deribit]

    options_okx = await okx.list_options("ETH")
    options_okx = [okx.to_option(inst) for inst in options_okx]

    options_common = [inst for inst in options_deribit if inst in options_okx]
    print(f"Common options: {options_common[0]}")

    quotes = [
        OptionQuote(
            option=option,
            highest_bid=None,
            lowest_ask=None,
        )
        for option in options_common
    ]




if __name__ == "__main__":
    asyncio.run(main())
