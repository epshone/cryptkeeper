from binance.enums import *
import time
import multiprocessing as mp
import logging


class aggregator_manager(object):
    """
    Manages all aggregators and triggers, facilitates the
    communication between the two.
    """
    def __init__(self, socket_manager):
        self.aggregators = {}
        self.conn_keys = []
        self.bm = socket_manager
        self.triggers = []
        logging.debug("Aggregator manager created.")

    def add_trigger_function(self, trigger):
        """Add a new trigger function to be managed by this manager."""
        self.triggers.append(trigger)

        for coin in trigger.coin_names:
            if coin not in self.aggregators:
                self._create_aggregator(coin)
        logging.debug("Trigger function added to manager.")

    def _create_aggregator(self, coin_name):
        """Create a new aggregator of a given coin's data."""
        new_aggregator = aggregator(socket_manager=self.bm, coin_name=coin_name)
        self.aggregators[coin_name] = aggregator
        logging.debug("Aggregator for " + coin_name + " created.")

    def _tick(self):
        """
        The logic that is performed each time after a
        predetermined delay.
        """
        self._evaluateTriggers()

    def _evaluateTriggers(self):
        for trigger in self.triggers:
            result = trigger._evaluate()
            if result is not None:
                trigger._action(result)


class aggregator(object):
    """
    Aggregates data about a given coin
    through the binance websocket manager.
    """

    def __init__(socket_manager, coin_name):
        """Initialize the aggregator class."""
        self._conn_keys = []
        self._bm = socket_manager
        self.coin_name = coin_name
        self._kline_data = []
        self._depth_data = []
        # Start the websockets and the socket manager
        self._open_kline_websocket()
        self._open_depth_websocket()
        self.bm.start()

    def _open_kline_websocket(self):
        """
        Open the KLine websocket and add the connection to the
        list of open connections.
        """
        conn_key = self._bm.start_kline_socket(self.coin_name,
                                               callback=self._aggregate_kline_data,
                                               interval=KLINE_INTERVAL_5MINUTE)
        self.conn_keys.append(conn_key)

    def _open_depth_socket(self):
        """
        Open the depth websocket and add the connection to the
        list of open connections.
        """
        conn_key = self._bm.start_depth_socket(self.coin_name,
                                               callback=self._aggregate_depth_data)
        self.conn_keys.append(conn_key)

    """Add the KLine data returned from the websocket to the KLine array"""
    def _aggregate_kline_data(self, data):
        self._kline_data.append(data)

    """Add the depth data returned from the websocket to the depth array"""
    def _aggregate_depth_data(self, data):
        self._depth_data.append(data)

    def get_all_kline_data(self):
        """
        Return all KLine data gathered by the
        websocket since it was opened.
        """
        return self._kline_data

    def get_all_depth_data(self):
        """
        Return all depth data gathered by the
        websocket since it was opened.
        """
        return self._depth_data

    def get_fields_from_kline(self, fields):
        """
        Return all KLine data filtered down to the given
        fields passed as an array.
        """
        result = []
        json = {}
        for data in self._kline_data:
            for field in fields:
                json[field] = data[field]
            result.append(json)
            json = {}
        return result

    def get_fields_from_depth(self, fields):
        """
        Return all depth data filtered down to the
        given fields passed as an array.
        """
        result = []
        json = {}
        for data in self._depth_data:
            for field in fields:
                json[field] = data[field]
            result.append(json)
            json = {}
        return result

    def close_all_connections(self):
        """Close all open websocket connections."""
        for conn_key in self.conn_keys:
            self.bm.stop_connection(conn_key)
        self.conn_keys = []


class trigger(object):
    """
    Base trigger class.

    Implementations override _evaluate(), _action().
    """

    def __init__(self, coin_names, refresh_seconds=1):
        self.coin_names = coin_names
        self.refresh_seconds = refresh_seconds

    # Should we take the action?
    def _evaluate(self):
        pass

    # Take the action when _evaluate() returns true
    def _action(self, params):
        pass

    # kill yoself
    def kill(self):
        # TODO: better?
        self.watching = False


class order(trigger):
    """
    Base order class.

    Implementations override _check_place_order(), _get_order_params().
    """

    def __init__(self, refresh_seconds=1, coin_names=None,
                 monitor_order_obj=None):
        super(order, self).__init__(refresh_seconds=refresh_seconds,
                                    coin_names=coin_names)
        self.monitor_order_obj = monitor_order_obj

    # Place the order and spawn a cancel order process if one is defined
    def _action(self, params):
        logging.debug(params)
        """if (self.monitor_order_obj is not None):
            self.monitor_order_obj.set_order_id(self.order_id)
            # spawn cancel_fn instance
            p = mp.Process(target=self.monitor_order_obj.watch)
            p.start()
            logging.debug("Cancel function instance started for order "
                          + str(self.order_id))
        """

    def _check_place_order(self, coin_info):
        pass

    def _evaluate(self):
        pass


# base order monitoring class
# implementations override _check_cancel_order()
class monitor_order(trigger):
    def __init__(self, refresh_seconds=1):
        super(monitor_order, self).__init__(refresh_seconds=refresh_seconds)

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
