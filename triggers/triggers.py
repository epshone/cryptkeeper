from binance.enums import *
import time
import multiprocessing as mp
import logging

"""Manages all aggregators and triggers, facilitates the
   communication between the two"""
class aggregator_manager(object):
    def __init__(self, socket_manager, coin_name):
        self.coin_name = coin_name
        self.aggregators = {}
        self.conn_keys = []
        self.bm = socket_manager
        self.triggers = []

    """Add a new trigger function to be managed by this manager"""
    def add_trigger_function(self, trigger):
        self.triggers.add(trigger)

        for coin in trigger.coin_names
            if coin not in aggregators:
                self._create_aggregator(coin)

    """Create a new aggregator of a given coin's data"""
    def _create_aggregator(self, coin_name):
        aggregator = aggregator(socket_manager=self.bm, coin_name=coin_name)
        self.aggregators[coin_name] = aggregator

    """The logic that is performed each time after a predetermined delay"""
    def _tick(self):
        self._evaluateTriggers()

    """Evaluate each trigger and perform the trigger action if the
       evaluation returns true"""
    def _evaluateTriggers(self):
        for trigger in self.triggers
            if trigger._evaluate():
                trigger._action()

"""Aggregates data about a given coin through the binance websocket manager"""
class aggregator(object):
    def __init__(socket_manager, coin_name):
        self._conn_keys = []
        self._bm = socket_manager
        self.coin_name = coin_name
        self._kline_data = []
        self._depth_data = []
        # Start the websockets and the socket manager
        self._open_kline_websocket()
        self._open_depth_websocket()
        self.bm.start()

    """Open the KLine websocket and add the connection to the
       list of open connections"""
    def _open_kline_websocket(self):
        conn_key = self._bm.start_kline_socket(self.coin_name, callback=self._aggregate_kline_data, interval=KLINE_INTERVAL_5MINUTE)
        self.conn_keys.append(conn_key)

    """Open the depth websocket and add the connection to the
       list of open connections"""
    def _open_depth_socket(self):
        conn_key = self._bm.start_depth_socket(self.coin_name, callback=self._aggregate_depth_data)
        self.conn_keys.add(conn_key)

    """Add the KLine data returned from the websocket to the KLine array"""
    def _aggregate_kline_data(self, data):
        self._kline_data.add(data)

    """Add the depth data returned from the websocket to the depth array"""
    def _aggregate_depth_data(self, data):
        self._depth_data.add(data)

    """Return all KLine data gathered by the websocket since it was opened"""
    def get_all_kline_data(self):
        return self._kline_data

    """Return all depth data gathered by the websocket since it was opened"""
    def get_all_depth_data(self):
        return self._depth_data

    """Return all KLine data filtered down to the given fields passed as an array"""
    def get_fields_from_kline(self, fields):
        result = []
        json = {}
        for data in self._kline_data:
            for field in fields:
                json[field] = data[field]
            result.add(json)
            json = {}
        return result

    """Return all depth data filtered down to the given fields passed as an array"""
    def get_fields_from_depth(self, fields):
        result = []
        json = {}
        for data in self._depth_data:
            for field in fields:
                json[field] = data[field]
            result.add(json)
            json = {}
        return result

    """Close all open websocket connections"""
    def close_all_connections(self):
        for conn_key in self.conn_keys
            self.bm.stop_connection(conn_key)
        self.conn_keys = []

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


    # How much and for what price should we place an order?
    def _get_order_params(self):
        pass

    # Place the order and spawn a cancel order process if one is defined
    def _action(self):
        params = self._get_order_params()
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
