from binance.websockets import BinanceSocketManager
from binance.enums import *
import time
import multiprocessing as mp
import logging


# Opens a websocket to continuosly gather coin information
class coin_info(object):
    def __init__(self, socket_manager, coin_name):
        self.coin_name = coin_name
        self.price_history = {}
        self.conn_key = None
        self.bm = socket_manager


    def open_kline_websocket(self):
        if self.conn_key is not None:
            self.close_connection()

        conn_key = self.bm.start_kline_socket(self.coin_info, callback=self.aggregate_price_data, interval=KLINE_INTERVAL_1MINUTE)
        self.bm.start()
        self.conn_key = conn_key


    def close_connection(self):
        self.bm.stop_connection(self.conn_key)
        self.conn_key = None


    def _aggregate_price_data(self, price):
        self.price_history.insert(0, price)



# base trigger class
# implementations override _evaluate(), _action()
class trigger(object):
    def __init__(self, api_client, refresh_seconds=1):
        self.refresh_seconds = refresh_seconds
        self.watching = True
        self.api_client = api_client

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
    def __init__(self, api_client, refresh_seconds=1, coin=None, monitor_order_obj=None):
        super(order, self).__init__(refresh_seconds=refresh_seconds,
                                    api_client=api_client)
        self.monitor_order_obj = monitor_order_obj
        self.monitor_order_obj.set_coin(coin)
        self.coin_i = coin_info(coin, api_client)
        # temporary for debugging
        self.order_id = 0

    # How much and for what price should we place an order?
    def _get_order_params(self):
        pass

    # Place the order and spawn a cancel order process if one is defined
    def _action(self):
        params = self._get_order_params()
        # Place the BUY order
        order = self.api_client.create_order(symbol=self.coin_i.coin_name, side=SIDE_BUY,
            type=ORDER_TYPE_LIMIT, timeInForce=TIME_IN_FORCE_GTC,
            quantity=params['amount'], price=params['price'])
        logging.debug(order)
        self.order_id = order['orderId']
        # Output order confirmation
        logging.debug("Order " + str(self.order_id)
                      + " placed: " + str(params['amount']) + " " + self.coin_i.coin_name
                      + " purchased at " + params['price'] + " each.")
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
        if(self._check_place_order(self.coin_i.get_coin_value())):
            self._action()


# base order monitoring class
# implementations override _check_cancel_order()
class monitor_order(trigger):
    def __init__(self, api_client, refresh_seconds=1):
        super(monitor_order, self).__init__(refresh_seconds=refresh_seconds,
                                            api_client=api_client)

    def set_order_id(self, order_id):
        self.order_id = order_id

    def set_coin(self, coin):
        self.coin_name = coin

    # has the order been completed already?
    def __check_complete(self):
        order = self.api_client.get_order(symbol=self.coin_name,
                                          orderId=self.order_id)
        logging.debug(order)
        return order['status'] == "COMPLETE"


    # Cancel the order
    def _action(self):
        result = self.api_client.cancel_order(symbol=self.coin_name,
                                              orderId=self.order_id)
        logging.debug("Order cancelled id:" + str(self.order_id))
        self.kill()

    # Should the order be cancelled?
    def _check_cancel_order(self):
        return False

    # check if its completed, and cancel the order if we should
    def _evaluate(self):
        self.__check_complete()
        if (self._check_cancel_order()):
            self._action()
