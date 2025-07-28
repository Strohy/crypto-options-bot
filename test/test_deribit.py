import pytest
from unittest.mock import AsyncMock, patch, MagicMock
from datetime import datetime
from options.base_exchange import Option, OptionQuoteUpdate
from options.deribit import Deribit


@pytest.mark.asyncio
async def test_connect():
    deribit = Deribit()
    with patch(
        "options.deribit.websockets.connect", new_callable=AsyncMock
    ) as mock_connect:
        await deribit.connect()
        mock_connect.assert_called_once_with("wss://www.deribit.com/ws/api/v2")
        assert deribit.ws == mock_connect.return_value


@pytest.mark.asyncio
async def test_send():
    deribit = Deribit()
    deribit.ws = AsyncMock()
    deribit.ws.recv = AsyncMock(return_value='{"key": "value"}')

    msg = {"jsonrpc": "2.0", "method": "test/method", "params": {}}
    response = await deribit._send(msg)

    deribit.ws.send.assert_awaited_once_with(
        '{"jsonrpc": "2.0", "method": "test/method", "params": {}}'
    )
    assert response == {"key": "value"}


@pytest.mark.asyncio
async def test_list_options_success():
    deribit = Deribit()
    deribit._send = AsyncMock(
        return_value={
            "result": [
                {"instrument_name": "ETH-21JUL25-3600-C"},
                {"instrument_name": "ETH-21JUL25-3700-P"},
            ]
        }
    )

    options = await deribit.list_options("ETH")
    assert len(options) == 2
    assert all(isinstance(opt, Option) for opt in options)
    assert options[0].strike == 3600
    assert options[1].option_type == "P"


@pytest.mark.asyncio
async def test_list_options_error():
    deribit = Deribit()
    deribit._send = AsyncMock(
        return_value={"error": {"code": 500, "message": "Server Error"}}
    )

    result = await deribit.list_options("ETH")
    assert result == {"code": 500, "message": "Server Error"}


@pytest.mark.asyncio
async def test_get_bid_ask():
    deribit = Deribit()
    option = Option("ETH", datetime.strptime("21JUL25", "%d%b%y").date(), 3600, "C")

    deribit._send = AsyncMock(
        return_value={"result": {"best_bid_price": 10.5, "best_ask_price": 11.0}}
    )

    quote = await deribit.get_bid_ask(option)
    assert isinstance(quote, OptionQuoteUpdate)
    assert quote.bid == 10.5
    assert quote.ask == 11.0
    assert quote.exchange == "deribit"


@pytest.mark.asyncio
async def test_subscribe_callback_invokes_function():
    deribit = Deribit()
    mock_function = MagicMock()
    response = {
        "params": {
            "data": {
                "instrument_name": "ETH-21JUL25-3600-C",
                "best_bid_price": 100.0,
                "best_ask_price": 110.0,
            }
        }
    }

    deribit.subscribe_callback(response, mock_function)
    mock_function.assert_called_once()
    result = mock_function.call_args[0][0]
    assert isinstance(result, OptionQuoteUpdate)
    assert result.bid == 100.0
    assert result.ask == 110.0


def test_to_option_and_from_option():
    deribit = Deribit()
    instrument = "ETH-21JUL25-3600-C"
    option = deribit.to_option(instrument)
    assert isinstance(option, Option)
    assert option.uly_currency == "ETH"
    assert option.expiry == datetime.strptime("21JUL25", "%d%b%y").date()
    assert option.strike == 3600
    assert option.option_type == "C"

    instrument_str = deribit.from_option(option)
    assert instrument_str == "ETH-21JUL25-3600-C"
