from triggers import order, monitor_order, aggregator
from datetime import datetime, timedelta
import time
import multiprocessing as mp
import logging
import sys
import json
from binance.client import Client
from binance.websockets import BinanceSocketManager
import input

# cancel after some number of seconds
class example_monitor_order(monitor_order):
    def __init__(self, seconds, api_client):
        super(example_monitor_order, self).__init__(api_client=api_client)
        self.seconds = seconds
        self.currtime = datetime.now()

    def _check_cancel_order(self):
        #if (datetime.now() >
        #        self.currtime + timedelta(seconds=self.seconds)):
            # cancel the order here
            return True


# example threshold trigger
class example_order(order):
    threshold = None

    def __init__(self, refresh_seconds, threshold,
                 api_client, monitor_obj):
        if monitor_obj is None:
            monitor_obj=example_monitor_order(seconds=2, api_client=api_client)
        super(example_order, self).__init__(refresh_seconds=refresh_seconds,
                                            coin=coin,
                                            monitor_order_obj=monitor_obj,
                                            api_client=api_client)
        self.threshold = threshold

    def _check_place_order(self, coin_info):
        if (coin_info > self.threshold):
            self.threshold += 100
            return True

    def _get_order_params(self):
        params = {
            "price": "0.0001",
            "amount": 200
        }
        return params


def startTrigger(socket_manager):
    triggers = []
    triggers.add(example_order(refresh_seconds=1, ))
    eth_usdt_agg = aggregator(socket_manager=socket_manager, coin_name='ETHUSDT'
                              order_triggers=e)
