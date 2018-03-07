from triggers import aggregator_manager, all_ticker, trigger
import logging
import time
from datetime import timedelta, datetime
import json
import multiprocessing as mp


ALL_TICKERS_AGGREGATOR = "ALL_COINS"


class test_aggregator_manager(aggregator_manager):
    def __init__(self):
        super(test_aggregator_manager, self).__init__(socket_manager=None)
        logging.debug("Test^^^")

    def _create_all_ticker(self):
        new_all_ticker = test_all_ticker()
        self.aggregators[ALL_TICKERS_AGGREGATOR] = new_all_ticker
        return new_all_ticker

    def _create_aggregator(self, coin_name):
        pass


class test_all_ticker(all_ticker):
    def __init__(self):
        super(test_all_ticker, self).__init__(socket_manager=None)
        logging.debug("Test All ticker created")
        self.go = True
        self._tick_freq = 0.25
        self.data = json.load(open('data.json'))
        self.i = 0
        p = mp.Process(target=self.aggregate)
        p.start()

    def aggregate(self):
        while self.go:
            time.sleep(self._tick_freq)
            self.ticker_data.append(self.data[self.i])
            logging.debug("data" + str(self.ticker_data))

    def close_connection(self, data):
        self.go = False


class order_tester(object):
    def __init__(self, order_class=None, monitor_class=None):
        self.watching = True
        self.order_class = order_class
        self.get_order_params_fn = order_class._get_order_params
        self.check_place_order_fn = order_class._check_place_order
        self.evaluate_fn = order_class._evaluate
        self.monitor_class = monitor_class

    def test(self, coin, start_datetime, end_datetime, refresh_rate):
        # TODO get info from API
        self.start_datetime = start_datetime
        self.end_datetime = end_datetime
        self.refresh_rate = refresh_rate
        self.curr_datetime = start_datetime
        self.info = {}

        self.balance = 1000

        self.testing_order_obj = self.order_class(refresh_seconds=refresh_rate,
                                                  coin=coin,
                                                  threshold=4)
        self.new_watch()

    def get_info_at_datetime(self):
        # get the coin info at self.curr_datetime
        return 13

    def new_evaluate(self):
        if(self.check_place_order_fn(self.testing_order_obj,
                                     self.get_info_at_datetime())):
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


class test_all_tickers(trigger):
    def __init__(self):
        super(test_all_tickers, self).__init__(coin_names=["ALL_COINS"])

    def _evaluate(self):
        data = self._aggregators["ALL_COINS"].get_ticker_data()
        logging.debug("in evaluate: " + str(data))

    def _action(self, params):
        logging.debug("ACTION")


def main():
    # tester = order_tester(test.example_order)
    # tester.test(coin="AION/ETH",
    #             start_datetime=datetime.now() - timedelta(seconds=10),
    #             end_datetime=datetime.now(),
    #             refresh_rate=1)
    logging.basicConfig(filename='output.log', level=logging.DEBUG)
    test_agg_manager = test_aggregator_manager()
    # test_fn = example_order(refresh_seconds=2,
    #                         coin_names=["ETHUSDT"],
    #                         threshold=1,
    #                         monitor_obj=None)
    test_fn = test_all_tickers()
    test_agg_manager.add_trigger_function(test_fn)
    test_agg_manager.start()
    logging.debug("done")


if __name__ == '__main__':
    logging.basicConfig(filename='output.log', level=logging.DEBUG)
    main()
