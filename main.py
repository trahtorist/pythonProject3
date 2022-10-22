from unicorn_binance_websocket_api.manager import BinanceWebSocketApiManager
import logging
import time
import threading
import os
import unicorn_fy
import order

unicornfy = unicorn_fy.UnicornFy()

logging.getLogger("unicorn_binance_websocket_api")
logging.basicConfig(level=logging.DEBUG,
                    filename=os.path.basename(__file__) + '.log',
                    format="{asctime} [{levelname:8}] {process} {thread} {module}: {message}",
                    style="{")
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
                #unicorn_fied_stream_data.update({"exch": "spot"})
                get_price(unicorn_fied_stream_data)


def print_stream_buffer_data_fut(binance_websocket_api_manager, stream_id):
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
                #print(unicorn_fied_stream_data)
                unicorn_fied_stream_data.update({"exch": "fut"})

                get_price(unicorn_fied_stream_data)


alice_api_key = "76dbde271bef0cdb741476db48ce46d5f3f75f6cc93444bbd66602694ca0f867"
alice_api_secret = "134eae46791bb51e569d4af8cd2ea08f52a0ca7be0db9e967b7d75ffec812a2a"
bob_api_key = "7tfcMnSKQd2FzQUZg7A6xkcr8zS9JHXiLri9TEsEmjTDIf6XRR5kk2Qyc5GFRwIC"
bob_api_secret = "0vFLSLlBi4m59B9zICEc5DpoBkWiuitYvIORULeXnQHMoKb6FzWZ7pvVqJICsWTZ"
#markets = ['ETHUSDT', "WOOUSDT"]
markets = ["WOOUSDT","JSTUSDT", "MDXUSDT", "GTCUSDT", "DUSKUSDT",  "REEFUSDT", "COTIUSDT",
        "MTLUSDT", "LITUSDT", "LINAUSDT", "MIRUSDT", "SUNUSDT", "LAZIOUSDT", "PORTOUSDT","JSTUSDT", "MKRUSDT", "SUNUSDT",
        "ANCUSDT", "DYDXUSDT","ETHUSDT","KLAYUSDT", "ATAUSDT",  "BTCDOMUSDT", "API3USDT","GMTUSDT",
          "AXSUSDT","KSMUSDT", "ENSUSDT", "UNIUSDT"]
channels = ['bookTicker']

dollars = 50
def get_price(prices_futures):

    #print(prices_futures)
    if "exch" in prices_futures:
        fut_data.update({prices_futures["symbol"]: prices_futures["best_bid_price"]})
    else:
        spot_data.update({prices_futures["symbol"]: prices_futures["best_bid_price"]})
    #print(spot_data, fut_data)
    #time.sleep(1)
    for k, v in fut_data.items():
        if k in spot_data.keys():
            #print(spot_data.keys())
            #if type(spot_data[k]) == str:
            pr = float(spot_data[k])
            res.setdefault(k, ((pr - float(v))/pr)*100)
            edata.update(res)
            sorted_prices = dict(sorted(edata.items(), key=lambda item: item[1]))
            ticker = str(max(sorted_prices.keys()))
            price_ticker = [max(sorted_prices.values()), max(sorted_prices.keys()), spot_data[ticker], fut_data[ticker]]
            get_signal(price_ticker)
            print(fut_data, spot_data)
def get_signal(data):
    if  (type(data[0]) == float):
        signal_data.update({"signal": data[0], "symbol": data[1], "price_spot": data[2], "price_fut": data[3]})
    if  (type(data[0]) == str):
        order_data = data
    else:
        order_data = []

    if len(signal_data) > 0 and xdata == {} or xdata['order_sent'] == "Kill_spot":
        qty = order.new_qty(dollars / float(signal_data["price_spot"]), signal_data["symbol"])
        #print(round(float(signal_data[2]), 2))
        price = order.new_price(signal_data["price_spot"], signal_data["symbol"])
        xdata.update({"order_sent": "BUY_SPOT_1", "symbol": signal_data["symbol"], "qty": qty})
        #order.new_order_spot(xdata["symbol"], "BUY", "LIMIT", qty, price)
        print("BUY_SPOT_1", order_data, xdata)
    if len(order_data) > 0:

        if order_data[5] == "NEW" and xdata['order_sent'] == 'BUY_SPOT_1':
            if xdata["symbol"] == signal_data["symbol"]:
                order.order_buy_move(order_data[4], order_data[2], order_data[6], price)

    #print(xdata,order_data, signal_data)
    if "order_sent" in xdata and len(order_data) > 0 and order_data[4] == "FILLED":

        if xdata['order_sent'] == 'BUY_SPOT_1' and order_data[0] == "order_spot":  #data[0] == "order_spot" and data[3] == "FILLED":
            if xdata["symbol"] == signal_data["symbol"]:
                print("SELL_FUT_2", order_data)
                price2 = order.new_price(signal_data["price_fut"], signal_data["symbol"])
                #order.new_order_fut(xdata["symbol"], "SELL", "LIMIT", xdata['qty'], price2)
                xdata.update({"order_sent": "SELL_FUT_2"})


        if xdata['order_sent'] == 'SELL_FUT_2'  and order_data[4] =="FILLED":
            xdata.update({"order_sent": "SELL_SPOT_3"})
            if xdata["symbol"] == signal_data["symbol"]:
                price3 = order.new_price(signal_data["price_spot"], xdata["symbol"])
                print("SELL SPOT 3", price3)
                order.new_order_spot(xdata["symbol"], "SELL", "LIMIT", xdata['qty'], price3)

        if xdata["order_sent"] == "SELL_SPOT_3" and order_data[0] =="order_spot":
            if xdata["symbol"] == signal_data["symbol"]:
                price4 = order.new_price(signal_data["price_spot"], xdata["symbol"])
                #order.new_order_fut(xdata["symbol"], "BUY", "LIMIT", xdata['qty'], price4)
                xdata.update({"order_sent": "SELL_SPOT_4"})
                print("SELL_SPOT_4")

if __name__ == '__main__':
    order.get_veracity()
    #time.sleep(4)

    binance_fut_api_manager = BinanceWebSocketApiManager(exchange="binance.com-futures")
    #fut_stream_id = binance_fut_api_manager.create_stream('arr', '!userData', stream_label="Futures-userData",
    #                                                    stream_buffer_name=True,
     #                                                   api_key=alice_api_key, api_secret=alice_api_secret)
    #worker_thread = threading.Thread(target=order.order_fut, args=(binance_fut_api_manager, fut_stream_id))
    #worker_thread.start()
    alice_stream_fut = binance_fut_api_manager.create_stream(channels, markets, stream_label="futures_price",
                                                         stream_buffer_name=True)
    worker_thread = threading.Thread(target=print_stream_buffer_data_fut, args=(binance_fut_api_manager,
                                                                                alice_stream_fut))
    worker_thread.start()


    binance_spot_api_manager = BinanceWebSocketApiManager(exchange="binance.com")

    #spot_stream_id = binance_spot_api_manager.create_stream('arr', '!userData', stream_label="SPOT-userData",
    #                                                   stream_buffer_name=True,
    #                                                  api_key=bob_api_key, api_secret=bob_api_secret)
    #worker_thread = threading.Thread(target=order.order_spot, args=(binance_spot_api_manager, spot_stream_id))
    #worker_thread.start()

    bob_stream_spot = binance_spot_api_manager.create_stream(channels, markets, stream_label="SPOT_price",
                                                             stream_buffer_name=True)
    worker_thread = threading.Thread(target=print_stream_buffer_data, args=(binance_spot_api_manager, bob_stream_spot))
    worker_thread.start()



#while True:
    #binance_spot_api_manager.print_summary()
    #binance_fut_api_manager.print_summary()

    #time.sleep(3)
