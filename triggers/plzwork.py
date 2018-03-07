from triggers import aggregator_manager, all_ticker, trigger
import logging
import time
from datetime import datetime
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
        self.data = json.load(open('./ticker_data/tickers_0.json'))
        p = mp.Process(target=self.aggregate)
        p.start()

    def aggregate(self):
        i = 0
        while self.go:
            data = self.data[i]["data"]
            self._aggregate_data(data)
            if(i+1 < len(self.data)):
                f = "%Y-%m-%d %H:%M:%S.%f"
                cur = self.data[i]["time"]
                nex = self.data[i+1]["time"]
                currTime = datetime.strptime(cur, f)
                nextTime = datetime.strptime(nex, f)
                delta = nextTime - currTime
                time.sleep(delta.total_seconds())
                i = i+1
            else:
                break

    def close_connection(self, data):
        self.go = False


class test_all_tickers(trigger):
    def __init__(self):
        super(test_all_tickers, self).__init__(coin_names=["ALL_COINS"])

    def _evaluate(self):
        data = self._aggregators["ALL_COINS"].get_ticker_data()
        logging.debug("in evaluate")

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
