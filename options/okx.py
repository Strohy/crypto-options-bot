import asyncio
import websockets
import json
from datetime import datetime
from .base_exchange import Exchange, OptionData
from okx.websocket.WsPublicAsync import WsPublicAsync
import okx.PublicData as PublicData
import okx.MarketData as MarketData


class OKX(Exchange):
    def __init__(self):
        self.url = "wss://ws.okx.com:8443/ws/v5/public"
        self.ws = None
        self.public_api = PublicData.PublicAPI(flag="0")
        self.market_api = MarketData.MarketAPI(flag="0")

    async def connect(self):
        self.ws = WsPublicAsync(url=self.url)
        await self.ws.start()

    async def list_options(self, currency: str = "ETH"):
        res = self.public_api.get_instruments(instType="OPTION", instFamily="ETH-USD")
        return [item["instId"] for item in res["data"]]

    async def get_bid_ask(self, instrument: str) -> OptionData:
        res = self.market_api.get_ticker(instId=instrument)
        return {
            "exchange": "okx",
            "symbol": "ETH",
            "option_type": instrument.split("-")[4],
            "strike": instrument.split("-")[3],
            "expiry": instrument.split("-")[2],
            "bid": res["data"][0]["bidPx"],
            "ask": res["data"][0]["askPx"],
            "instrument_name": instrument,
            "timestamp": datetime.now().isoformat(),
        }

    async def subscribe_bid_ask(self, instruments: list[str]):
        args = [
            {"channel": "tickers", "instId": instrument} for instrument in instruments
        ]
        while True:
            await self.ws.subscribe(args, callback=self.subscribeCallback)
            while True:
                await asyncio.sleep(3600)

    def subscribeCallback(self, raw):
        message = json.loads(raw)

        if "data" in message:
            update = message["data"][0]
            instrument_name = update.get("instId")
            bid = update.get("bidPx")
            ask = update.get("askPx")
            timestamp = datetime.now().isoformat()

            print(
                {
                    "exchange": "okx",
                    "instrument_name": instrument_name,
                    "bid": bid,
                    "ask": ask,
                    "timestamp": timestamp,
                }
            )


async def main():
    okx = OKX()
    await okx.connect()

    instruments = ["ETH-USD-250721-3600-C"]
    # options = await okx.list_options("ETH"); print(options)
    # bid_ask = await okx.get_bid_ask(instruments[0]); print(bid_ask)
    await okx.subscribe_bid_ask(instruments)


asyncio.run(main())
