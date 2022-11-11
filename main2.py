import asyncio
import json

import websocket
from unicorn_binance_websocket_api.manager import BinanceWebSocketApiManager
import logging
import time
import threading
import os
import unicorn_fy
import order2
import queue
unicornfy = unicorn_fy.UnicornFy()


xdata = {}

price_ticker = []
spot_data = {}
fut_data = {}
edata = {}
signal_data = {}
quantityPrecision = {}
pricePrecision = {}
res = dict()


def print_stream_buffer_data(binance_websocket_api_manager, stream_id):

    while True:

        if binance_websocket_api_manager.is_manager_stopping():
            exit(0)
        oldest_stream_data_from_stream_buffer = binance_websocket_api_manager.pop_stream_data_from_stream_buffer(
            stream_id)

        if oldest_stream_data_from_stream_buffer is False:
            time.sleep(0.01)
        else:
            unicorn_fied_stream_data = unicornfy.binance_websocket(oldest_stream_data_from_stream_buffer)

            if "best_bid_price" in unicorn_fied_stream_data:

                get_price(unicorn_fied_stream_data)


def print_stream_buffer_data_fut(binance_websocket_api_manager, stream_id):
    print(binance_websocket_api_manager, "_^..^_", stream_id)
    while True:
        if binance_websocket_api_manager.is_manager_stopping():

            exit(0)
        oldest_stream_data_from_stream_buffer = binance_websocket_api_manager.pop_stream_data_from_stream_buffer(
                  stream_id)

        #print("oldest_stream_data_from_stream_buffer", binance_websocket_api_manager,threading.current_thread().name)
        if oldest_stream_data_from_stream_buffer is False:
            time.sleep(0.01)
        else:

            unicorn_fied_stream_data = unicornfy.binance_com_websocket(oldest_stream_data_from_stream_buffer)
            if "best_bid_price" in unicorn_fied_stream_data:

                unicorn_fied_stream_data.update({"exch": "fut"})

                get_price(unicorn_fied_stream_data)


alice_api_key = "76dbde271bef0cdb741476db48ce46d5f3f75f6cc93444bbd66602694ca0f867"
alice_api_secret = "134eae46791bb51e569d4af8cd2ea08f52a0ca7be0db9e967b7d75ffec812a2a"
bob_api_key = "7tfcMnSKQd2FzQUZg7A6xkcr8zS9JHXiLri9TEsEmjTDIf6XRR5kk2Qyc5GFRwIC"
bob_api_secret = "0vFLSLlBi4m59B9zICEc5DpoBkWiuitYvIORULeXnQHMoKb6FzWZ7pvVqJICsWTZ"
markets = ['ETHUSDT', 'XRPUSDT', 'LTCUSDT', 'TRXUSDT', 'BNBUSDT',"YFIIUSDT"]
#markets = ["WOOUSDT","JSTUSDT", "MDXUSDT", "GTCUSDT", "DUSKUSDT",  "REEFUSDT", "COTIUSDT",
       # "MTLUSDT", "LITUSDT", "LINAUSDT", "MIRUSDT", "SUNUSDT", "LAZIOUSDT", "PORTOUSDT","JSTUSDT", "MKRUSDT", "SUNUSDT",
       # "ANCUSDT", "DYDXUSDT","ETHUSDT","KLAYUSDT", "ATAUSDT",  "BTCDOMUSDT", "API3USDT","GMTUSDT",
       #   "AXSUSDT","KSMUSDT", "ENSUSDT", "UNIUSDT"]
channels = ['bookTicker']


def order_fut(binance_fut_api_manager, fut_stream_id):

    while True:
        if binance_fut_api_manager.is_manager_stopping():
            exit(0)
        oldest_stream_data_from_stream_buffer = binance_fut_api_manager.pop_stream_data_from_stream_buffer(
            fut_stream_id)

        if oldest_stream_data_from_stream_buffer is False:
            time.sleep(0.01)
        else:
            unicorn_fied_stream_data = unicornfy.binance_futures_websocket(oldest_stream_data_from_stream_buffer)

            if "event_type" in unicorn_fied_stream_data:
                if unicorn_fied_stream_data["event_type"] == "ORDER_TRADE_UPDATE":  # ACCOUNT_UPDATE
                    order_spo = ["order_fut",
                             unicorn_fied_stream_data["side"],
                             unicorn_fied_stream_data["symbol"],
                             unicorn_fied_stream_data["order_id"],
                             unicorn_fied_stream_data["current_order_status"],
                             unicorn_fied_stream_data["order_quantity"],
                             unicorn_fied_stream_data["order_price"],
                             unicorn_fied_stream_data["event_type"],
                             unicorn_fied_stream_data["unicorn_fied"][0]]

                    if unicorn_fied_stream_data["current_order_status"] == "NEW":
                        print("Новая заявка фьючерс ", unicorn_fied_stream_data["side"])
                    if unicorn_fied_stream_data["current_order_status"] == "FILLED":
                        print("Заявка на фьючерс исполнена ", unicorn_fied_stream_data["side"])
                    if unicorn_fied_stream_data["current_order_status"] == "PARTIALLY_FILLED":
                        print("Заявка на фьючерс исполнена частично",
                              unicorn_fied_stream_data["last_executed_quantity"],
                              unicorn_fied_stream_data["cumulative_filled_quantity"])

                    if unicorn_fied_stream_data["current_order_status"] == "CANCELED":
                        print("Заявка на фьючерс отменено", unicorn_fied_stream_data["side"])
                    get_signal(order_spo)
                if unicorn_fied_stream_data["event_type"] == "ACCOUNT_UPDATE":
                    print("balances:", unicorn_fied_stream_data["balances"][0]["asset"],
                          unicorn_fied_stream_data["balances"][0]["wallet_balance"])
                    if unicorn_fied_stream_data["positions"] != []:
                        order = [{'symbol': unicorn_fied_stream_data["positions"][0]["symbol"],
                             "entry_price": unicorn_fied_stream_data["positions"][0]["entry_price"],
                             "position_amount": unicorn_fied_stream_data["positions"][0]["position_amount"],
                             "upnl": unicorn_fied_stream_data["positions"][0]["upnl"]}]

                        get_signal(order)

def order_spot(binance_spot_api_manager, stream_id):

    while True:
        if binance_spot_api_manager.is_manager_stopping():
            exit(0)
        oldest_stream_data_from_stream_buffer = binance_spot_api_manager.pop_stream_data_from_stream_buffer(
            stream_id)
        if oldest_stream_data_from_stream_buffer is False:
            time.sleep(0.01)
        else:
            unicorn_fied_stream_data = unicornfy.binance_websocket(oldest_stream_data_from_stream_buffer)
            #print(unicorn_fied_stream_data)
            if "event_type" in unicorn_fied_stream_data:
                if unicorn_fied_stream_data["event_type"] == "executionReport":
                    order_spo = ["order_spot",
                             unicorn_fied_stream_data["side"],
                             unicorn_fied_stream_data["symbol"],
                             unicorn_fied_stream_data["order_id"],
                             unicorn_fied_stream_data["current_order_status"],
                             unicorn_fied_stream_data["order_quantity"],
                             unicorn_fied_stream_data["order_price"],
                             unicorn_fied_stream_data["event_type"],
                             unicorn_fied_stream_data["unicorn_fied"][0]]
                    get_signal(order_spo)

                    if unicorn_fied_stream_data["current_order_status"] == "NEW":
                        print("Новая заявка спот ", unicorn_fied_stream_data["side"])

                    if unicorn_fied_stream_data["current_order_status"] == "FILLED":
                        print("Заявка спот исполнена ", unicorn_fied_stream_data["side"])



                #if unicorn_fied_stream_data["event_type"] == ["outboundAccountPosition"]:
                    #print(unicorn_fied_stream_data["balances"][0]["free"],
                       # unicorn_fied_stream_data["balances"][0]["asset"])

def set_spread(k,spot_price,fut_price):
    pr = float(spot_price)
    res.setdefault(k, ((pr - float(fut_price)) / pr) * 100)
    return res
import collections
from queue import Queue
dollars = 50

locker = threading.RLock()
def get_price(prices_futures):
    #locker.release()
    res={}
    #locker.acquire()
    #print(threading.current_thread().name, prices_futures)
    #if "stream_type" in prices_futures:
    if "symbol" in prices_futures:
        spot_data.update({prices_futures["symbol"]: prices_futures["best_bid_price"]})
        #print("Thread-8")
    if "result" in prices_futures:
        ticker = prices_futures['result']["s"]
        fut_data.update({ticker.translate({ord(i): None for i in '_'}): prices_futures["result"]["a"]})
        #print(fut_data)


    for k, v in fut_data.items():
        if k in spot_data.keys():

            res.setdefault(k, ((float(spot_data[k]) - float(v))/float(spot_data[k]))*100)
            edata.update(res)
            sorted_prices = dict(sorted(edata.items(), key=lambda item: item[1]))

            [last] = collections.deque(sorted_prices, maxlen=1)
            #print(edata)
            get_signal([sorted_prices[last], last, spot_data[last], fut_data[last]])

def get_signal(data):
    print(data)
    #time.sleep(1)
    if  (type(data[0]) == float):
        signal_data.update({"signal": data[0], "symbol": data[1], "price_spot": data[2], "price_fut": data[3]})

    if  (type(data[0]) == str):
        order_data = data
        #print("str order_data", order_data)
        if order_data[0] == "order_spot" and order_data[4] == "FILLED" and xdata == {}:
            ddata = {"order_spot_status": "FILLED"}
            xdata.update({'order_sent': 'BUY_SPOT_1'})

    if (type(data[0]) == dict):
        positions_futures = data
        #print("dict", positions_futures)
        order_data = []
    else:
        order_data = []

    #старт

    if len(signal_data) > 0 and xdata == {} and signal_data["signal"]>0.9:
        qty = order2.new_qty_spot(dollars / float(signal_data["price_spot"]), signal_data["symbol"])
        price = order2.new_price(signal_data["price_spot"], signal_data["symbol"])
        #price2 = order2.new_price(signal_data["price_fut"], signal_data["symbol"])
        print(signal_data["signal"])
        print("BUY_SPOT_1", signal_data["symbol"], price)
        front_price = order2.new_price_spot((float(price)*0.01)/100, signal_data["symbol"])
        act_price = float(price) + float(front_price)
        print(float(front_price)+float(price))
        xdata.update({"order_sent": "BUY_SPOT_1", "symbol": signal_data["symbol"], "qty": qty, "price": act_price})
        order2.new_order_spot(xdata["symbol"], "BUY", "LIMIT", qty, price)

    #if "order_spot_status" in xdata:
        print("старт", order_data)
        #print("хеджируем", order_data, xdata)
        #if order_data[4] == "FILLED" and xdata['order_sent'] == 'BUY_SPOT_1' and float(xdata["price"])<float(signal_data["price_spot"]):
           # price3 = order.new_price(signal_data["price_spot"], signal_data["symbol"])
           # print("order_buy_move", xdata, price3)
            #order.order_buy_move(order_data[4], order_data[2], order_data[6], price3)
            #xdata.update({"order_sent": "order_buy_move"})
        # хеджируем позицию
    if 'order_sent' in xdata:
        if xdata['order_sent'] == 'BUY_SPOT_1':  #data[0] == "order_spot" and data[3] == "FILLED":
            if xdata["symbol"] == signal_data["symbol"]:

                xdata.update({"order_sent": "SELL_FUT_2", "order_spot_status": "expect"})
                price2 = signal_data["price_fut"]
                front_price2 =order2.new_price(float(price2) - (float(price2) * 0.01) / 100, signal_data["symbol"])
                #act_price2 = float(price2)-float(front_price)
                print(xdata['order_sent'], "SELL_FUT_2", signal_data["symbol"], price2,"-",front_price2)
                order2.new_order_fut(xdata["symbol"], "SELL", "LIMIT", xdata['qty'], front_price2)
                print(xdata["symbol"], signal_data["symbol"])
        if xdata['order_sent'] == 'SELL_FUT_2':
            if xdata["symbol"] == signal_data["symbol"]:
                xdata.update({"order_sent": "SELL_SPOT_3"})
                price3 = signal_data["price_spot"]
                front_price3 =order2.new_price_spot(float(price3) - (float(price3) * 0.01) / 100, signal_data["symbol"])
                print(front_price3, "SELL_SPOT_3", xdata["symbol"], price3, xdata["order_sent"])
                ord = order2.new_order_spot(xdata["symbol"], "SELL", "LIMIT", xdata['qty'], front_price3)
                print(ord,"new_order_spot")

        if xdata["order_sent"] == "SELL_SPOT_3":
            if xdata["symbol"] == signal_data["symbol"]:
                xdata.update({"order_sent": "BUY_FUT_4"})
                price4 = order2.new_price(signal_data["price_spot"], xdata["symbol"])
                front_price4 =order2.new_price(float(price4) + (float(price4) * 0.01) / 100, signal_data["symbol"])
                order2.new_order_fut(xdata["symbol"], "BUY", "LIMIT", xdata['qty'], front_price4)
                print("BUY_FUT_4", xdata["symbol"], front_price4)
def on_message(ws, message):
    data = json.loads(message)

    #print(data)
    tick = data['result']["s"]
    symb = {"gate":"gate","symbol": tick.translate({ord(i): None for i in '_'}), "best_bid_price": data['result']['b'],
              "best_ask_price": data['result']['a']}

    get_price(data)
    #print(data)


def re_markets():
    ff= []
    for i in order2.market:
        ff.append(i.translate({ord(i): None for i in '_'}))
    return ff

def on_close(ws):
    print("### closed ###")
def on_error(ws,message):
    print(message)

def on_open(ws):
    ws.send(json.dumps({
        "time": int(time.time()),
        "channel": "futures.book_ticker",
        "event": "subscribe",  # "unsubscribe" for unsubscription
        "payload": order2.market}))
def  get_start_gate():
    ws = websocket.WebSocketApp("wss://fx-ws.gateio.ws/v4/ws/usdt",
                                on_message=on_message,
                                on_close=on_close,
                                on_open=on_open)

    ws.run_forever()
    print("get_start_gate")
def get_start_binance():
    binance_fut_api_manager = BinanceWebSocketApiManager(exchange="binance.com-futures")

    alice_stream_fut = binance_fut_api_manager.create_stream(channels, re_markets(), stream_label="futures_price",
                                                         stream_buffer_name=True)
    worker_thread6 = threading.Thread(target=print_stream_buffer_data_fut, args=(binance_fut_api_manager,
                                                                                alice_stream_fut))
    worker_thread6.start()

if __name__ == '__main__':
    #order.get_veracity()
    #time.sleep(4)
    binance_spot_api_manager_testnet = BinanceWebSocketApiManager(exchange="binance.com-testnet")

    spot_stream_id_testnet = binance_spot_api_manager_testnet.create_stream('arr', '!userData',
                                                                            stream_label="SPOT-userData_testnet",
                                                                            stream_buffer_name=True,
                                                                            api_key=bob_api_key,
                                                                            api_secret=bob_api_secret)
    worker_thread4 = threading.Thread(target=order_spot, args=(binance_spot_api_manager_testnet, spot_stream_id_testnet))
    worker_thread4.start()
    # _________________futures________
    #binance_fut_api_manager_testnet = BinanceWebSocketApiManager(exchange="binance.com-futures-testnet")

    #fut_stream_id_testnet = binance_fut_api_manager_testnet.create_stream('arr', '!userData',
    #                                                                      stream_label="Futures-userData_testnet",
    #                                                                      stream_buffer_name=True,
    #                                                                      api_key=alice_api_key,
    #                                                                      api_secret=alice_api_secret)
    #worker_thread3 = threading.Thread(target=order_fut, args=(binance_fut_api_manager_testnet, fut_stream_id_testnet))
    #worker_thread3.start()


    #fut_stream_id = binance_fut_api_manager.create_stream('arr', '!userData', stream_label="Futures-userData",
    #                                                    stream_buffer_name=True,
    #                                                    api_key=alice_api_key, api_secret=alice_api_secret)
    #worker_thread = threading.Thread(target=order.order_fut, args=(binance_fut_api_manager, fut_stream_id))
    #worker_thread.start()



    binance_spot_api_manager = BinanceWebSocketApiManager(exchange="binance.com")

    #spot_stream_id = binance_spot_api_manager.create_stream('arr', '!userData', stream_label="SPOT-userData",
    #                                                  stream_buffer_name=True,
    #                                                 api_key=bob_api_key, api_secret=bob_api_secret)
    #worker_thread = threading.Thread(target=order.order_spot, args=(binance_spot_api_manager, spot_stream_id))
    #worker_thread.start()

    #bob_stream_spot = binance_spot_api_manager.create_stream(channels, re_markets(), stream_label="SPOT_price",
      #                                                           stream_buffer_name=True)
    #worker_thread = threading.Thread(target=print_stream_buffer_data, args=(binance_spot_api_manager, bob_stream_spot))
    #worker_thread.start()
    binance_fut_api_manager = BinanceWebSocketApiManager(exchange="binance.com-futures")

    alice_stream_fut = binance_fut_api_manager.create_stream(channels, re_markets(), stream_label="futures_price",
                                                         stream_buffer_name=True)
    worker_thread = threading.Thread(target=print_stream_buffer_data_fut, args=(binance_fut_api_manager,
                                                                                alice_stream_fut))
    worker_thread.start()
    get_start_gate()


    worker_thread = threading.Thread(target=get_start_gate, daemon = True)
    worker_thread.start()


    print(threading.current_thread().name)


#while True:
    #binance_spot_api_manager.print_summary()
    #binance_fut_api_manager.get_active_stream_list
    #binance_fut_api_manager_testnet.print_summary()
    #binance_spot_api_manager_testnet.print_summary()
    #time.sleep(3)