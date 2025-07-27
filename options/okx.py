import asyncio
import json
from datetime import datetime
from .base_exchange import Exchange, OptionQuoteUpdate, Option
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

    async def list_options(self, currency: str = "ETH") -> list[Option]:
        api_response = self.public_api.get_instruments(
            instType="OPTION", instFamily="ETH-USD"
        )
        return [self.to_option(inst["instId"]) for inst in api_response["data"]]

    async def get_bid_ask(self, instrument: Option) -> OptionQuoteUpdate:
        instrument = self.from_option(instrument)
        api_response = self.market_api.get_ticker(instId=instrument)
        return OptionQuoteUpdate(
            exchange="okx",
            bid=api_response["data"][0]["bidPx"],
            ask=api_response["data"][0]["askPx"],
        )

    async def subscribe_bid_ask(self, instruments: list[Option], function):
        instruments = [self.from_option(option) for option in instruments]
        args = [
            {"channel": "tickers", "instId": instrument} for instrument in instruments
        ]

        callback_with_handler = lambda raw: self.subscribe_callback(
            raw, function
        )
        while True:
            await self.ws.subscribe(args, callback=callback_with_handler)
            while True:
                await asyncio.sleep(3600)

    def subscribe_callback(self, raw, function):
        response = json.loads(raw)

        if "data" in response:
            update = response["data"][0]
            instrument_name = update.get("instId")
            bid_price = update.get("bidPx")
            ask_price = update.get("askPx")

            function(
                OptionQuoteUpdate(
                    exchange="okx",
                    option_id=self.to_option(instrument_name).id(),
                    bid=float(bid_price) if bid_price else None,
                    ask=float(ask_price) if ask_price else None,
                )
            )

    def to_option(self, instrument_str: str) -> Option:
        parts = instrument_str.split("-")
        return Option(
            uly_currency=parts[0],
            expiry=self._to_date(parts[2]),
            strike=int(parts[3]),
            option_type=parts[4],
        )

    def _to_date(self, date_str: str) -> datetime.date:
        """Convert date string to datetime.date object."""
        return datetime.strptime(date_str, "%y%m%d").date()

    def from_option(self, option) -> str:
        return (
            f"{option.uly_currency}-USD"
            f"-{option.expiry.strftime('%y%m%d')}"
            f"-{option.strike}"
            f"-{option.option_type}"
        )


async def main():
    okx = Okx()
    await okx.connect()

    instruments = ["ETH-USD-250721-3600-C"]
    # options = await okx.list_options("ETH"); print(options)
    # bid_ask = await okx.get_bid_ask(instruments[0]); print(bid_ask)
    # await okx.subscribe_bid_ask(instruments)

    option = okx.to_option(instruments[0])
    print(okx.from_option(option))


if __name__ == "__main__":
    asyncio.run(main())
