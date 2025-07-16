import asyncio
import json
import websockets

msg = {
    "id": 8772,
    "jsonrpc": "2.0",
    "method": "public/get_order_book",
    "params": {"depth": 5, "instrument_name": "BTC-PERPETUAL"},
}

async def call_api(msg):
    async with websockets.connect("wss://test.deribit.com/ws/api/v2") as websocket:
        await websocket.send(msg)  # already serialized
        response = await websocket.recv()
        print(response)


if __name__ == "__main__":
    asyncio.run(call_api(json.dumps(msg)))
