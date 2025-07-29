import pytest
import json
from unittest.mock import patch, AsyncMock, MagicMock
from datetime import datetime
from options.base_exchange import Exchange, OptionQuoteUpdate, Option
from okx.websocket.WsPublicAsync import WsPublicAsync
from options.okx import Okx
from options.base_exchange import Option, OptionQuoteUpdate


@pytest.mark.asyncio
async def test_connect():
    okx = Okx()
    with patch("options.okx.WsPublicAsync", new_callable=MagicMock) as mock_ws:
        instance = mock_ws.return_value
        instance.start = AsyncMock()
        await okx.connect()
        instance.start.assert_awaited_once()
        assert okx.ws == instance


@patch("options.okx.PublicData.PublicAPI")
@pytest.mark.asyncio
async def test_list_options(mock_public_api):
    mock_api_instance = mock_public_api.return_value
    mock_api_instance.get_instruments.return_value = {
        "data": [
            {"instId": "ETH-USD-250721-3600-C"},
            {"instId": "ETH-USD-250721-3700-P"},
        ]
    }

    okx = Okx()
    options = await okx.list_options("ETH")
    assert len(options) == 2
    assert options[0].strike == 3600
    assert options[1].option_type == "P"


@patch("options.okx.MarketData.MarketAPI")
@pytest.mark.asyncio
async def test_get_bid_ask(mock_market_api):
    mock_api_instance = mock_market_api.return_value
    mock_api_instance.get_ticker.return_value = {
        "data": [{"bidPx": "120.5", "askPx": "121.0"}]
    }

    okx = Okx()
    option = Option("ETH", datetime.strptime("250721", "%y%m%d").date(), 3600, "C")
    result = await okx.get_bid_ask(option)

    assert isinstance(result, OptionQuoteUpdate)
    assert result.bid == 120.5
    assert result.ask == 121.0
    assert result.exchange == "okx"


def test_subscribe_callback_invokes_function():
    okx = Okx()
    mock_function = MagicMock()
    raw = json.dumps(
        {
            "data": [
                {"instId": "ETH-USD-250721-3600-C", "bidPx": "100.0", "askPx": "105.0"}
            ]
        }
    )

    okx.subscribe_callback(raw, mock_function)
    mock_function.assert_called_once()
    result = mock_function.call_args[0][0]
    assert isinstance(result, OptionQuoteUpdate)
    assert result.bid == 100.0
    assert result.ask == 105.0


def test_to_option_and_from_option():
    okx = Okx()
    instrument = "ETH-USD-250721-3600-C"
    option = okx.to_option(instrument)
    assert isinstance(option, Option)
    assert option.uly_currency == "ETH"
    assert option.expiry == datetime.strptime("250721", "%y%m%d").date()
    assert option.strike == 3600
    assert option.option_type == "C"

    instrument_str = okx.from_option(option)
    assert instrument_str == "ETH-USD-250721-3600-C"
