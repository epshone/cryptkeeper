from triggers import order, monitor_order, aggregator_manager, aggregator
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
    def __init__(self, seconds):
        super(example_monitor_order, self).__init__()
        self.seconds = seconds
        self.currtime = datetime.now()

    def _check_cancel_order(self):
        return True


# example threshold trigger
class example_order(order):
    threshold = None

    def __init__(self, refresh_seconds, coin_names, threshold,
                 monitor_obj):
        super(example_order, self).__init__(refresh_seconds=refresh_seconds,
                                            coin_names=coin_names,
                                            monitor_order_obj=monitor_obj)
        self.threshold = threshold

    def _check_place_order(self, coin):
        prices = self._aggregators[coin].get_prices()
        if(len(prices) < 2):
            return False
        if(prices[0]-prices[1] > self.threshold):
            logging.debug(str(prices[0]) + " " + str(prices[1]))
            return False


def startTrigger(socket_manager):
    agg_manager = aggregator_manager(socket_manager)
    agg_manager.add_trigger_function(example_order(refresh_seconds=2,
                                                   coin_names=["ETHUSDT"],
                                                   threshold=1,
                                                   monitor_obj=None))
    agg_manager.start()
