from triggers import order, monitor_order
from datetime import datetime, timedelta
import time
import multiprocessing as mp
import logging
import sys
import json
from binance.client import Client
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

    def __init__(self, refresh_seconds, coin, threshold,
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


def main():
    logging.basicConfig(filename='output.log', level=logging.DEBUG)

    api_key = ""
    api_secret = ""
    try:
        credentials = json.load(open("./credentials.json"))
        api_key = credentials['API_KEY']
        api_secret = credentials['API_SECRET']
    except IOError:
        try:
            credentials = json.load(open("../credentials.json"))
            api_key = credentials['API_KEY']
            api_secret = credentials['API_SECRET']
        except IOError:
            api_key = str(raw_input("Enter your public Binance API key: "))
            api_secret = str(raw_input("Enter your secret Binance API key: "))

    cli = input.CommandLineInterface(api_key=api_key,api_secret=api_secret)
    cli.cmdloop()

    # api_client = Client(api_key, api_secret)
    #
    # orderer = example_order(refresh_seconds=1, coin="AIONETH",
    #                         threshold=0, api_client=api_client, monitor_obj=None)
    #
    # # need the comma after the string otherwise python takes the input
    # # as a list of characters...
    # p = mp.Process(target=orderer.watch)
    # p.start()
    # x = mp.Process(target=orderer.watch)
    # x.start()
    # v = mp.Process(target=orderer.watch)
    # v.start()
    # while(True):
    #     time.sleep(5)
    #     logging.debug("parent still kickin")


if __name__ == '__main__':
    main()
