from unicorn_binance_websocket_api.manager import BinanceWebSocketApiManager
import logging
import time
import threading
import os
import unicorn_fy
unicornfy = unicorn_fy.UnicornFy()

logging.getLogger("unicorn_binance_websocket_api")
logging.basicConfig(level=logging.DEBUG,
                    filename=os.path.basename(__file__) + '.log',
                    format="{asctime} [{levelname:8}] {process} {thread} {module}: {message}",
                    style="{")


def print_stream_buffer_data(binance_websocket_api_manager, stream_id):
    while True:
        if binance_websocket_api_manager.is_manager_stopping():
            exit(0)
        oldest_stream_data_from_stream_buffer = binance_websocket_api_manager.pop_stream_data_from_stream_buffer(stream_id)
        if oldest_stream_data_from_stream_buffer is False:
            time.sleep(0.01)
        else:
            unicorn_fied_stream_data = unicornfy.binance_com_websocket(oldest_stream_data_from_stream_buffer)

            print(unicorn_fied_stream_data, "SPOT")

def print_stream_buffer_data_fut(binance_websocket_api_manager, stream_id):
    while True:
        if binance_websocket_api_manager.is_manager_stopping():
            exit(0)
        oldest_stream_data_from_stream_buffer = binance_websocket_api_manager.pop_stream_data_from_stream_buffer(stream_id)
        if oldest_stream_data_from_stream_buffer is False:
            time.sleep(0.01)
        else:
            print(binance_websocket_api_manager)
            unicorn_fied_stream_data = unicornfy.binance_com_futures_websocket(oldest_stream_data_from_stream_buffer)  #binance_com_websocket(oldest_stream_data_from_stream_buffer)
            print(unicorn_fied_stream_data,"FUT")

# create instances of BinanceWebSocketApiManager
binance_fut_api_manager = BinanceWebSocketApiManager(exchange="binance.com-futures-testnet")

# configure api key and secret for binance.com for Alice
alice_api_key = "76dbde271bef0cdb741476db48ce46d5f3f75f6cc93444bbd66602694ca0f867"
alice_api_secret = "134eae46791bb51e569d4af8cd2ea08f52a0ca7be0db9e967b7d75ffec812a2a"
# create the userData streams
markets = ["ethusdt"]
channels = ['bookTicker']
alice_stream_id = binance_fut_api_manager.create_stream('arr', '!userData', stream_label="Futures",
                                                                  stream_buffer_name=True,
                                                                  api_key=alice_api_key, api_secret=alice_api_secret)

worker_thread = threading.Thread(target=print_stream_buffer_data_fut, args=(binance_fut_api_manager,
                                                                       alice_stream_id))
worker_thread.start()


bob_api_key = "7tfcMnSKQd2FzQUZg7A6xkcr8zS9JHXiLri9TEsEmjTDIf6XRR5kk2Qyc5GFRwIC"
bob_api_secret = "0vFLSLlBi4m59B9zICEc5DpoBkWiuitYvIORULeXnQHMoKb6FzWZ7pvVqJICsWTZ"
# create the userData streams
binance_spot_api_manager = BinanceWebSocketApiManager(exchange="binance.com-testnet")
bob_stream_id = binance_spot_api_manager.create_stream('arr', '!userData', stream_label="SPOT",
                                                                stream_buffer_name=True,
                                                                api_key=bob_api_key, api_secret=bob_api_secret)

worker_thread = threading.Thread(target=print_stream_buffer_data, args=(binance_spot_api_manager, bob_stream_id))
worker_thread.start()

bob_stream_spot = binance_spot_api_manager.create_stream(channels, markets, stream_label="SPOT_price", stream_buffer_name=True)
worker_thread = threading.Thread(target=print_stream_buffer_data, args=(binance_spot_api_manager,
                                                                       bob_stream_spot))
worker_thread.start()

alice_stream_fut = binance_fut_api_manager.create_stream(channels, ["ethusdt"], stream_label="futures_price", stream_buffer_name=True)
worker_thread = threading.Thread(target=print_stream_buffer_data_fut, args=(binance_fut_api_manager,
                                                                        alice_stream_fut))
worker_thread.start()
# monitor the streams
#while True:
    #binance_fut_api_manager.print_summary()
    #binance_spot_api_manager.print_summary()
    #time.sleep(1)