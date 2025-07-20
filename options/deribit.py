import asyncio
import websockets
import json
from datetime import datetime
from .base_exchange import Exchange, OptionData


class Deribit(Exchange):
    def __init__(self):
        self.url = "wss://www.deribit.com/ws/api/v2"
        self.ws = None

    async def connect(self):
        self.ws = await websockets.connect(self.url)

    async def _send(self, msg: dict) -> dict:
        await self.ws.send(json.dumps(msg))
        response = await self.ws.recv()
        return json.loads(response)

    async def list_options(self, currency: str = "ETH"):
        msg = {
            "id": 8772,
            "jsonrpc": "2.0",
            "method": "public/get_instruments",
            "params": {"currency": currency, "kind": "option", "expired": False},
        }
        res = await self._send(msg)
        if res.get("result") is not None:
            return [instr["instrument_name"] for instr in res["result"]]
        return res["error"]

    async def get_bid_ask(self, instrument: str) -> OptionData:
        msg = {
            "id": 8772,
            "jsonrpc": "2.0",
            "method": "public/ticker",
            "params": {"instrument_name": instrument},
        }
        res = await self._send(msg)
        data = res.get("result", {})
        return {
            "exchange": "deribit",
            "symbol": "ETH",
            "option_type": instrument.split("-")[3],
            "strike": instrument.split("-")[2],
            "expiry": instrument.split("-")[1],
            "bid": data.get("best_bid_price"),
            "ask": data.get("best_ask_price"),
            "instrument_name": instrument,
            "timestamp": datetime.now().isoformat(),
        }

    async def subscribe_bid_ask(self, instruments: list[str]):
        channels = [f"quote.{i}" for i in instruments]
        msg = {
            "jsonrpc": "2.0",
            "method": "public/subscribe",
            "id": 42,
            "params": {"channels": channels},
        }
        await self.ws.send(json.dumps(msg))

        while True:
            raw = await self.ws.recv()
            message = json.loads(raw)
            self.subscribeCallback(message)

    def subscribeCallback(self, message):
        if "params" in message:
            update = message["params"]["data"]
            instrument_name = update["instrument_name"]
            bid = update.get("best_bid_price")
            ask = update.get("best_ask_price")
            timestamp = datetime.now().isoformat()

            # Change print to processing and update logic
            print(
                {
                    "exchange": "deribit",
                    "instrument_name": instrument_name,
                    "bid": bid,
                    "ask": ask,
                    "timestamp": timestamp,
                }
            )


async def main():
    deribit = Deribit()
    await deribit.connect()

    instruments = ["ETH-21JUL25-3600-C"]
    # options = await deribit.list_options(); print(options)
    # bid_ask = await deribit.get_bid_ask(instruments[0]); print(bid_ask)
    await deribit.subscribe_bid_ask(instruments)


asyncio.run(main())
