import asyncio
import json
from datetime import datetime
from .base_exchange import Exchange, OptionData, Option
from okx.websocket.WsPublicAsync import WsPublicAsync
import okx.PublicData as PublicData
import okx.MarketData as MarketData


class Okx(Exchange):
    def __init__(self):
        self.url = "wss://ws.okx.com:8443/ws/v5/public"
        self.ws = None
        self.public_api = PublicData.PublicAPI(flag="0")
        self.market_api = MarketData.MarketAPI(flag="0")

    async def connect(self):
        self.ws = WsPublicAsync(url=self.url)
        await self.ws.start()

    async def list_options(self, currency: str = "ETH"):
        api_response = self.public_api.get_instruments(instType="OPTION", instFamily="ETH-USD")
        return [inst["instId"] for inst in api_response["data"]]

    async def get_bid_ask(self, instrument: str) -> OptionData:
        api_response = self.market_api.get_ticker(instId=instrument)
        return {
            "exchange": "okx",
            "symbol": "ETH",
            "option_type": instrument.split("-")[4],
            "strike": instrument.split("-")[3],
            "expiry": instrument.split("-")[2],
            "bid": api_response["data"][0]["bidPx"],
            "ask": api_response["data"][0]["askPx"],
            "instrument_name": instrument,
            "timestamp": datetime.now().isoformat(),
        }

    async def subscribe_bid_ask(self, instruments: list[str]):
        args = [
            {"channel": "tickers", "instId": instrument} for instrument in instruments
        ]
        while True:
            await self.ws.subscribe(args, callback=self.subscribe_callback)
            while True:
                await asyncio.sleep(3600)

    def subscribe_callback(self, raw):
        response = json.loads(raw)

        if "data" in response:
            update = response["data"][0]
            instrument_name = update.get("instId")
            bid_price = update.get("bidPx")
            ask_price = update.get("askPx")
            timestamp = datetime.now().isoformat()

            print(
                {
                    "exchange": "okx",
                    "instrument_name": instrument_name,
                    "bid": bid_price,
                    "ask": ask_price,
                    "timestamp": timestamp,
                }
            )

    def to_option(self, instrument_str: str) -> Option:
        parts = instrument_str.split("-")
        return {
            "uly_currency": parts[0],
            "expiry": self._to_date(parts[2]),
            "strike": int(parts[3]),
            "option_type": parts[4],
        }
    
    def _to_date(self, date_str: str) -> datetime.date:
        """Convert date string to datetime.date object."""
        return datetime.strptime(date_str, "%y%m%d").date()

async def main():
    okx = Okx()
    await okx.connect()

    instruments = ["ETH-USD-250721-3600-C"]
    # options = await okx.list_options("ETH"); print(options)
    # bid_ask = await okx.get_bid_ask(instruments[0]); print(bid_ask)
    # await okx.subscribe_bid_ask(instruments)

    options = await okx.list_options("ETH")
    op0 = okx.to_option(options[0]); print(op0)


if __name__ == "__main__":
    asyncio.run(main())
