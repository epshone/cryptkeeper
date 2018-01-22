import sys
sys.path.insert(0, r'/Users/EvanShone/git/cryptkeeper')
import triggers.test as test
import logging
from datetime import timedelta, datetime


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
        logging.debug("Order " + str(8) + " placed: "
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
    tester = order_tester(test.example_order)
    tester.test(coin="AION/ETH",
                start_datetime=datetime.now() - timedelta(seconds=10),
                end_datetime=datetime.now(),
                refresh_rate=1)
    logging.debug("done")


if __name__ == '__main__':
    logging.basicConfig(filename='output.log', level=logging.DEBUG)
    main()
