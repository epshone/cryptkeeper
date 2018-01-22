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
        self.monitor_class = order_class.monitor_class

    def test(self, start_datetime, end_datetime, refresh_rate):
        # TODO get info from API
        self.start_datetime = start_datetime
        self.end_datetime = end_datetime
        self.refresh_rate = refresh_rate
        self.curr_datetime = start_datetime
        self.info = {}

        self.balance = 1000

        self.new_watch()

    def get_info_at_datetime(self):
        # get the coin info at self.curr_datetime
        return 5

    def new_evaluate(self):
        if(self.check_place_order_fn(self.get_info_at_datetime())):
            self.new_action()

    def new_action(self):
        logging.debug("Order " + str(8)
                      + " placed: " + self.get_order_params_fn())

    def new_watch(self):
        while(self.watching):
            delta = timedelta(seconds=self.seconds)
            self.curr_datetime = self.curr_datetime + delta
            if (self.curr_datetime > self.end_datetime):
                return

            if(self.new_evaluate()):
                self.new_action()


def main():
    tester = order_tester(test.example_order)
    tester.test(datetime.now() - timedelta(seconds=10), datetime.now(), 1)
    logging.debug("done")


if __name__ == '__main__':
    main()
