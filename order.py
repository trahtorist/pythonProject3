import json
import math
from datetime import datetime
from binance.helpers import round_step_size

from binance.client import Client
#from  binance.exceptions import ClientError
import pandas as pd
import time
import main
from pandas import DataFrame
spot_api_key = "7tfcMnSKQd2FzQUZg7A6xkcr8zS9JHXiLri9TEsEmjTDIf6XRR5kk2Qyc5GFRwIC"
spot_api_secret = "0vFLSLlBi4m59B9zICEc5DpoBkWiuitYvIORULeXnQHMoKb6FzWZ7pvVqJICsWTZ"

fut_api_key = '76dbde271bef0cdb741476db48ce46d5f3f75f6cc93444bbd66602694ca0f867'
fut_api_secret = '134eae46791bb51e569d4af8cd2ea08f52a0ca7be0db9e967b7d75ffec812a2a'

client_fut = Client(fut_api_key, fut_api_secret, testnet=True)


client_spot = Client(spot_api_key, spot_api_secret)#, testnet=True)
client_spot.API_URL = "https://api1.binance.com" #"https://testnet.binance.vision"
#print(client_spot.API_URL )
pd.set_option('display.max_rows', 500)
pd.set_option('display.max_columns', 500)
pd.set_option('display.width', 1000)
xdata = {}
def order_buy_move(id,ticker,price_order,price):
    if price_order < price:
        client_spot.cancel_order_spot(symbol=ticker, orderId=id)
        xdata.update({"order_sent": "Kill_spot"})
        print("order_buy_move", xdata)

def new_price (price2, symbol2):
    #print("new_price", price2, symbol2, pricePrecision[symbol2])
    new_qt = "{:0.0{}f}".format(float(price2), pricePrecision[symbol2])
    return new_qt
def new_qty(qty2, symbol2):
    #print(qty2, symbol2, quantityPrecision[symbol2])
    new_ro = "{:0.0{}f}".format(float(qty2), quantityPrecision[symbol2])
    #print(new_ro)
    return new_ro
def get_veracity():
    info = client_fut.futures_exchange_info()
    quantityPrecision.update({si['symbol']: si['quantityPrecision'] for si in info['symbols'] if si['symbol'] in markets})
    pricePrecision.update({si['symbol']: si['pricePrecision'] for si in info['symbols'] if si['symbol'] in markets})
    info2 = client_spot.get_exchange_info() # futures_exchange_info()
    PRICE_FILTER.update({si['symbol']: si['filters'][0]["minPrice"]  for si in info2['symbols'] if si['symbol'] in markets})
    LOT_SIZE.update({si['symbol']: si['filters'][2]["stepSize"] for si in info2['symbols'] if si['symbol'] in markets})

def new_order_fut(symbol, side, type, quantity, price):
    #print("send order futures", quantity, price, symbol)
    client_fut.futures_create_order(symbol=symbol, side=side, type=type,
                                    quantity=quantity, price=price, timeInForce="GTC")

def new_order_spot(symbol, side, type, quantity, price):
    print("отправил спот ордер__",price)
    client_spot.create_order(symbol=symbol, side=side, type=type, quantity=quantity,
                             price=price, timeInForce="GTC")


def cancel_order_spot(symbol,orderId):
    client_spot.cancel_order(symbol=symbol, orderId=orderId, timestamp=True)

def cancel_order_fut(symbol,orderId):
    print("cancel order futures")
    client_fut.cancel_order(symbol=symbol, orderId=orderId, timestamp=True)


def top_coin():
    all_tickers = pd.DataFrame(client_spot.get_ticker())
    usdt = all_tickers[all_tickers.symbol.str.contains("USDT")]
    work = usdt[~((usdt.symbol.str.contains("UP")) | (usdt.symbol.str.contains("DOWN")))]
    print(work)
    top_coin = work[work.priceChangePercent == work.priceChangePercent.max()]
    top_coin = top_coin.symbol.values[0]
    return top_coin


class str2(str):
    def __repr__(self):
        return ''.join(('"', super().__repr__()[1:-1], '"'))
markets = ["WOOUSDT","JSTUSDT", "MDXUSDT", "GTCUSDT", "DUSKUSDT",  "REEFUSDT", "COTIUSDT","BTCUSDT",
        "MTLUSDT", "LITUSDT", "LINAUSDT", "MIRUSDT", "SUNUSDT", "LAZIOUSDT", "PORTOUSDT","JSTUSDT", "MKRUSDT", "SUNUSDT",
        "ANCUSDT", "DYDXUSDT","ETHUSDT","KLAYUSDT", "ATAUSDT",  "BTCDOMUSDT", "API3USDT","GMTUSDT",
           "AXSUSDT","KSMUSDT", "ENSUSDT", "UNIUSDT","TRXUSDT", "BNBUSDT", "LTCUSDT", "XRPUSDT"]
quantityPrecision = {}
pricePrecision = {}
PRICE_FILTER={}
LOT_SIZE={}

def new_qty_spot(old_qty, symbol2):
    qty = str(float(LOT_SIZE[symbol2])*math.floor(float(old_qty)/ float(LOT_SIZE[symbol2])))
    return qty

def new_price_spot (old_price, symbol2):
    price = str(float(PRICE_FILTER[symbol2])*math.floor(float(old_price)/ float(PRICE_FILTER[symbol2])))
    return price

if __name__ == '__main__':
    get_veracity()
    #print(quantityPrecision, pricePrecision)
    #xdata = {}
    #new_order_fut("BTCUSDT", "BUY", "LIMIT", "0.18", "20946")

    #print(PRICE_FILTER, LOT_SIZE)
    #info2 = client_spot.get_exchange_info()  # futures_exchange_info()
    #for si in info2['symbols'] :
    #    print(si['symbol'])
    #for order in client_spot.get_open_orders):
       # cancel_order_spot(symbol="BNBUSDT", orderId=order["orderId"])
        #print(order)
    #cancel_order_spot(symbol="ETHUSDT",orderId ="2753763")

    #print(
    #data = client_fut.futures_exchange_info()
    #info = data['symbols']
    #for x in range(len(info)):  # find length of list and run loop
    #print(data)

    #spot_orders = pd.DataFrame(client_spot.get_all_orders(symbol="BNBUSDT"), columns=['orderId', 'type', 'side', 'price', 'status'])
    #fut_orders = pd.DataFrame(client_fut.futures_get_all_orders(symbol="BTCUSDT"),  columns=['orderId', 'type', 'side', 'price', 'status'])
    #print(fut_orders)
    #print(fut_orders)
    #cancel_order_fut(symbol="ETHUSDT", orderId="959546411")
    #client_fut.API_URL = 'https://testnet.binancefuture.com'


    #new_order_fut("ETHUSDT", "SELL", "LIMIT", "0.01", "1250")
    #client_fut_balance = client_fut.futures_account_balance()
    #print(client_fut_balance)
    #print(top_coin())
    #spot_balance = client_spot.get_asset_balance(asset='USDT')['free']

    #spot_balance_eth = client_spot.get_asset_balance(asset='ETH')['free']
    #print(spot_balance, spot_balance_eth)
    #print(client_spot_balance)
    #open_order = client_fut.get_open_orders()
    #print("open orders :", open_order)
    #new_order()

    #try:

        # print(f"* exchange_info {symbol}* ", cl.exchange_info(symbol), sep="\n")

        # print(f"* best_price {symbol}* ", cl.book_ticker(symbol=symbol), sep="\n")
        # buy_price = cl.book_ticker(symbol=symbol).get('askPrice')
        # sell_price = cl.book_ticker(symbol=symbol).get('bidPrice')




    #print(f"* account assets * ", client_fut.futures_account(), sep="\n")

        # order_id = 8214572
        # print(f"* CANCEL order {order_id}", cl.cancel_order(symbol=symbol, orderId=order_id), sep="\n")

        #df = DataFrame(client.get_all_orders(symbol, recvWindow=59000), columns=['price', 'origQty', 'executedQty', 'cummulativeQuoteQty', 'origQuoteOrderQty', 'status', 'type', 'side', 'orderId'])
        #print("* ORDERS *", df.tail(10), sep="\n")

   # except ClientError as e:
       # print(e.error_code, e.error_message)
