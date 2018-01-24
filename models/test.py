import triggers.test as test
import logging
from datetime import timedelta, datetime
from binance.client import Client
from binance import helpers
import json


class order_tester(object):
    def __init__(self, client, order_class=None, monitor_class=None):
        self.watching = True
        self.order_class = order_class
        self.get_order_params_fn = order_class._get_order_params
        self.check_place_order_fn = order_class._check_place_order
        self.evaluate_fn = order_class._evaluate
        self.monitor_class = monitor_class
        self.client = client

    def test(self, coin, start_date, end_date, interval):
        # TODO get info from API
        self.start_datetime = start_date
        self.end_datetime = end_date
        self.refresh_rate = interval
        self.curr_datetime = start_date
        self.klines = self.client.get_historical_klines(coin,
                                                        interval,
                                                        start_date,
                                                        end_date)
        self.index = 0

        logging.debug(self.klines)
        self.balance = 1000

        self.testing_order_obj = self.order_class(refresh_seconds=interval,
                                                  coin=coin,
                                                  threshold=5)
        self.new_watch()

    def get_next_info(self):
        if self.index >= len(self.klines):
            # TODO get more clines
            pass
        val = self.klines[self.index]
        self.index += 1
        return val

    def new_evaluate(self):
        if(self.check_place_order_fn(self.testing_order_obj,
                                     self.get_next_info())):
            self.new_action()

    def new_action(self):
        logging.debug("test Order " + str(8) + " placed: "
                      + self.get_order_params_fn(self.testing_order_obj))

    def new_watch(self):
        while(self.watching):
            logging.debug("in")
            delta = timedelta(seconds=self.refresh_rate)
            self.curr_datetime = self.curr_datetime + delta
            if (self.curr_datetime > self.end_datetime):
                return

            if(self.new_evaluate()):
                self.new_action()


def main():
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

    api_client = Client(api_key, api_secret)

    tester = order_tester(client=api_client, order_class=test.example_order)
    tester.test(coin="AIONETH",
                start_date="1 Dec, 2017",
                end_date="1 Jan, 2018",
                interval=Client.KLINE_INTERVAL_1MINUTE)
    logging.debug("done")


if __name__ == '__main__':
    logging.basicConfig(filename='output.log', level=logging.DEBUG)
    main()
