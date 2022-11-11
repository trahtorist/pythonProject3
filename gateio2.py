import asyncio
import threading
import time
import json
import main2
import websocket
# pip install websocket_client
from websocket import create_connection

import main2
import order2

def on_message(ws, message):
    data =  json.loads(message)

    #print(data)
    tick = data['result']["s"]
    symb = {"ticker": tick.translate({ord(i): None for i in '_'}), "bid": data['result']['b'],
              "ask": data['result']['a']}
    order.get_price(str(symb))
    #print(data)


def re_markets():
    ff= []
    for i in order.market:
        ff.append(i.translate({ord(i): None for i in '_'}))
    return ff
print(re_markets())
def on_close(ws):
    print("### closed ###")
def on_error(ws,message):
    print(message)

def on_open(ws):
    ws.send(json.dumps({
        "time": int(time.time()),
        "channel": "futures.book_ticker",
        "event": "subscribe",  # "unsubscribe" for unsubscription
        "payload": order.market}))
def  get_starter():
    ws = websocket.WebSocketApp("wss://fx-ws.gateio.ws/v4/ws/usdt",
                                on_message=on_message,
                                on_close=on_close,
                                on_open=on_open)
    print("gdsfghsdf")
    ws.run_forever()



if __name__ == '__main__':
    get_starter()