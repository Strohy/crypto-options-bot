from options.deribit import Deribit
from options.okx import Okx
from functools import reduce
from options.base_exchange import Option
import asyncio

exchange_registry = {
    "Deribit": Deribit,
    "Okx": Okx,
}


class Aggregator:
    def __init__(self, exchange_list: list[str]):
        self.exchanges = [
            exchange_registry[exchange_name]() for exchange_name in exchange_list
        ]

    async def connect(self):
        for exchange in self.exchanges:
            await exchange.connect()

    async def common_options(self) -> list[Option]:
        all_opt = [await ex.list_options("ETH") for ex in self.exchanges]
        common_opt = list(reduce(set.intersection, map(set, all_opt)))
        return common_opt

    async def subscribe_bid_ask(self, instruments: list[Option], function):
        tasks = [
            asyncio.create_task(ex.subscribe_bid_ask(instruments, function))
            for ex in self.exchanges
        ]
        await asyncio.gather(*tasks)
