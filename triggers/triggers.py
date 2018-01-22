import time
import multiprocessing as mp
import logging


# data about a coin, just filler info
# TODO: make this real info
class coin_info(object):
    def __init__(self, coin_name):
        self.coin_name = coin_name
        self.value = 0

    def get_coin_info(self):
        self.value += 1
        logging.debug(self.coin_name + "price:" + str(self.value))
        return self.value


# base trigger class
# implementations override _evaluate(), _action()
class trigger(object):
    def __init__(self, refresh_seconds=1):
        self.refresh_seconds = refresh_seconds
        self.watching = True

    # Should we take the action?
    def _evaluate(self):
        pass

    # Take the action when _evaluate() returns true
    def _action(self):
        pass

    # evaluate after every interval
    def watch(self):
        while(self.watching):
            time.sleep(self.refresh_seconds)
            if(self._evaluate()):
                self._action()

    # kill yoself
    def kill(self):
        # TODO: better?
        self.watching = False


# base order class
# implementations override _check_place_order(), _get_order_params()
class order(trigger):
    def __init__(self, refresh_seconds=1, coin=None, monitor_order_obj=None):
        super(order, self).__init__(refresh_seconds)
        self.monitor_order_obj = monitor_order_obj
        self.coin_i = coin_info(coin)
        # temporary for debugging
        self.order_id = 0

    # How much and for what price should we place an order?
    def _get_order_params(self):
        pass

    # Place the order and spawn a cancel order process if one is defined
    def _action(self):
        self.order_id += 1
        logging.debug("Order " + str(self.order_id)
                      + " placed: " + self._get_order_params())
        if (self.monitor_order_obj is not None):
            self.monitor_order_obj.set_order_id(self.order_id)
            # spawn cancel_fn instance
            p = mp.Process(target=self.monitor_order_obj.watch)
            p.start()
            logging.debug("Cancel function instance started for order "
                          + str(self.order_id))

    def _check_place_order(self, coin_info):
        pass

    def _evaluate(self):
        if(self._check_place_order(self.coin_i.get_coin_info())):
            self._action()


# base order monitoring class
# implementations override _check_cancel_order()
class monitor_order(trigger):
    def __init__(self, refresh_seconds=1):
        super(monitor_order, self).__init__(refresh_seconds)

    def set_order_id(self, order_id):
        self.order_id = order_id

    # has the order been completed already?
    def __check_complete(self):
        # TODO
        # order is completed
        if (self.order_id == 99999999):
            logging.debug("Order Completed")
            self.kill()

    # Cancel the order
    def _action(self):
        # TODO
        logging.debug("Order cancelled id:" + str(self.order_id))
        self.kill()

    # Should the order be cancelled?
    def _check_cancel_order(self):
        pass

    # check if its completed, and cancel the order if we should
    def _evaluate(self):
        self.__check_complete()
        if (self._check_cancel_order()):
            self._action()
