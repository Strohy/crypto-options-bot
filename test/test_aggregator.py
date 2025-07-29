from datetime import date
import asyncio
import pytest
from unittest.mock import AsyncMock, patch
from options.base_exchange import Option
from options.aggregator import Aggregator

def test_aggregator_initialization():

    agg = Aggregator(["Deribit", "Okx"])
    assert len(agg.exchanges) == 2
    assert type(agg.exchanges[0]).__name__ in ["Deribit", "Okx"]


@pytest.mark.asyncio
async def test_aggregator_connect():
    with patch(
        "options.aggregator.Deribit.connect", new_callable=AsyncMock
    ) as deribit_connect, patch(
        "options.aggregator.Okx.connect", new_callable=AsyncMock
    ) as okx_connect:

        agg = Aggregator(["Deribit", "Okx"])
        await agg.connect()

        deribit_connect.assert_awaited_once()
        okx_connect.assert_awaited_once()


@pytest.mark.asyncio
async def test_common_options():
    option = Option("ETH", date(2025, 7, 25), 2500, "C")

    with patch(
        "options.aggregator.Deribit.list_options", new_callable=AsyncMock
    ) as mock_deribit_list, patch(
        "options.aggregator.Okx.list_options", new_callable=AsyncMock
    ) as mock_okx_list:

        mock_deribit_list.return_value = [option]
        mock_okx_list.return_value = [option]

        agg = Aggregator(["Deribit", "Okx"])
        common = await agg.common_options()

        assert common == [option]
        mock_deribit_list.assert_awaited_once()
        mock_okx_list.assert_awaited_once()


@pytest.mark.asyncio
async def test_subscribe_bid_ask():
    option = Option("ETH", date(2025, 7, 25), 2500, "C")

    with patch(
        "options.aggregator.Deribit.subscribe_bid_ask", new_callable=AsyncMock
    ) as deribit_sub, patch(
        "options.aggregator.Okx.subscribe_bid_ask", new_callable=AsyncMock
    ) as okx_sub:

        deribit_sub.return_value = asyncio.Future()
        deribit_sub.return_value.set_result(None)
        okx_sub.return_value = asyncio.Future()
        okx_sub.return_value.set_result(None)

        agg = Aggregator(["Deribit", "Okx"])
        await agg.subscribe_bid_ask([option], function=lambda x: x)

        deribit_sub.assert_awaited_once()
        okx_sub.assert_awaited_once()
