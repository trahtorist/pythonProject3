import time
import json

import websocket
# pip install websocket_client
from websocket import create_connection
def on_message(ws, message):
    data = json.loads(message)

    try:
        print(data)
        symb = data['result']["s"]
        print(f"{symb.translate({ord(i): None for i in '_'})} = {data['result'][0]['last']}:")
    except:
        print(message)

def on_close(ws):
    print("### closed ###")
def on_error(ws,message):
    print(message)

def on_open(ws):
    ws.send(json.dumps({
        "time": int(time.time()),
        "channel": "futures.book_ticker",
        "event": "subscribe",  # "unsubscribe" for unsubscription
        "payload": ["BTC_USDT"]}))


if __name__ == '__main__':
    ws = websocket.WebSocketApp("wss://fx-ws.gateio.ws/v4/ws/usdt",
                                on_message=on_message,
                                on_close=on_close,
                                on_error=on_error)
    ws.on_open = on_open
    ws.run_forever()