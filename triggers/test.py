from triggers import order, monitor_order
from datetime import datetime, timedelta
import time
import multiprocessing as mp
import logging


# cancel after some number of seconds
class example_monitor_order(monitor_order):
    def __init__(self, seconds):
        super(example_monitor_order, self).__init__()
        self.seconds = seconds
        self.currtime = datetime.now()

    def _check_cancel_order(self):
        if (datetime.now() >
                self.currtime + timedelta(seconds=self.seconds)):
            # cancel the order here
            return True


# example threshold trigger
class example_order(order):
    threshold = None

    def __init__(self, refresh_seconds, coin, threshold,
                 monitor_obj=example_monitor_order(2)):
        super(example_order, self).__init__(refresh_seconds, coin, monitor_obj)
        self.threshold = threshold

    def _check_place_order(self, coin_info):
        if (coin_info > self.threshold):
            self.threshold += 5
            return True

    def _get_order_params(self):
        s = self.coin_i.coin_name + " @ " + str(self.coin_i.value)
        return s


def main():
    logging.basicConfig(filename='output.log', level=logging.DEBUG)

    orderer = example_order(refresh_seconds=1, coin="ETH/AION",
                            threshold=5)

    # need the comma after the string otherwise python takes the input
    # as a list of characters...
    p = mp.Process(target=orderer.watch)
    p.start()
    while(True):
        time.sleep(5)
        logging.debug("parent still kickin")


if __name__ == '__main__':
    main()
