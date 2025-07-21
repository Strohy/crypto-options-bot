import asyncio
import websockets
import json
from datetime import datetime
from .base_exchange import Exchange, OptionData, Option


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
        api_response = await self._send(msg)
        if api_response.get("result") is not None:
            return [instr["instrument_name"] for instr in api_response["result"]]
        return api_response["error"]

    async def get_bid_ask(self, instrument: str) -> OptionData:
        msg = {
            "id": 8772,
            "jsonrpc": "2.0",
            "method": "public/ticker",
            "params": {"instrument_name": instrument},
        }
        api_response = await self._send(msg)
        data = api_response.get("result", {})
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
            self.subscribe_callback(message)

    def subscribe_callback(self, response):
        if "params" in response:
            update = response["params"]["data"]
            instrument_name = update["instrument_name"]
            bid_price = update.get("best_bid_price")
            ask_price = update.get("best_ask_price")
            timestamp = datetime.now().isoformat()

            # Change print to processing and update logic
            print(
                {
                    "exchange": "deribit",
                    "instrument_name": instrument_name,
                    "bid": bid_price,
                    "ask": ask_price,
                    "timestamp": timestamp,
                }
            )

    def to_option(self, instrument_str: str) -> Option:
        """Convert instrument string to Option."""
        parts = instrument_str.split("-")
        return {
            "uly_currency": parts[0],
            "expiry": self._to_date(parts[1]),
            "strike": int(parts[2]),
            "option_type": parts[3],
        }

    def _to_date(self, date_str: str) -> datetime.date:
        """Convert date string to datetime.date object."""
        return datetime.strptime(date_str, "%d%b%y").date()


async def main():
    deribit = Deribit()
    await deribit.connect()

    instruments = ["ETH-21JUL25-3600-C"]
    # options = await deribit.list_options("ETH"); print(options)
    # bid_ask = await deribit.get_bid_ask(instruments[0]); print(bid_ask)
    # await deribit.subscribe_bid_ask(instruments)
    
    options = await deribit.list_options("ETH")
    op0 = deribit.to_option(options[0]); print(op0)


if __name__ == "__main__":
    asyncio.run(main())
