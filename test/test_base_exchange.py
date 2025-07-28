import pytest
from datetime import date
from options.base_exchange import Option, OptionQuoteUpdate, Exchange
from unittest.mock import AsyncMock
import dataclasses


def test_option_equality_and_immutability():
    opt1 = Option(
        uly_currency="ETH", expiry=date(2025, 12, 31), strike=2000, option_type="C"
    )
    opt2 = Option(
        uly_currency="ETH", expiry=date(2025, 12, 31), strike=2000, option_type="C"
    )
    opt3 = Option(
        uly_currency="ETH", expiry=date(2025, 12, 31), strike=2500, option_type="P"
    )

    assert opt1 == opt2
    assert opt1 != opt3

def test_option_immutability():
    opt = Option(
        uly_currency="ETH", expiry=date(2025, 12, 31), strike=2000, option_type="C"
    )
    with pytest.raises(dataclasses.FrozenInstanceError):
        opt.strike = 2100


def test_option_quote_update_optional_fields():
    option = Option(
        uly_currency="ETH", expiry=date(2025, 12, 31), strike=2000, option_type="C"
    )
    update = OptionQuoteUpdate(
        exchange="TestExchange", option=option, bid=None, ask=2500.5
    )

    assert update.exchange == "TestExchange"
    assert update.bid is None
    assert update.ask == 2500.5


@pytest.mark.asyncio
async def test_exchange_mock_methods():
    mock_exchange = Exchange()
    mock_exchange.connect = AsyncMock()
    mock_exchange.list_options = AsyncMock(
        return_value=[Option("ETH", date(2025, 12, 31), 2000, "C")]
    )
    mock_exchange.get_bid_ask = AsyncMock(
        return_value=OptionQuoteUpdate(
            exchange="MockEx",
            option=Option("ETH", date(2025, 12, 31), 2000, "C"),
            bid=100.0,
            ask=120.0,
        )
    )

    await mock_exchange.connect()
    options = await mock_exchange.list_options("ETH")
    quote = await mock_exchange.get_bid_ask("ETH-31DEC25-2000-C")

    assert len(options) == 1
    assert options[0].strike == 2000
    assert quote.bid == 100.0
    assert quote.ask == 120.0
