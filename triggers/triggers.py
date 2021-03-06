from binance.enums import *
import multiprocessing as mp
import time
import logging

ALL_TICKERS_AGGREGATOR = "ALL_COINS"


class order(object):
    def __init__(self, price, amount, time):
        self.price = price
        self.amount = amount
        self.time = time


class coin_orders(object):
    """
    the price of a coin at a time
    """
    def __init__(self, coin):
        self.coin = coin
        self.orders = []

    def place_order(self, order):
        self.orders.append(order)

    def get_orders(self):
        return self.orders


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
        self.paused = False
        self._tick_freq = 0.1
        logging.debug("Aggregator manager created.")

    def start(self):
        self.paused = False
        self._tick()

    def add_trigger_function(self, trigger):
        """Add a new trigger function to be managed by this manager."""
        self.triggers.append(trigger)
        result = {}

        for coin in trigger.coin_names:
            if coin not in self.aggregators:
                aggregator = None
                if coin == ALL_TICKERS_AGGREGATOR:
                    aggregator = self._create_all_ticker()
                else:
                    aggregator = self._create_aggregator(coin)

                result[coin] = aggregator
        trigger.set_aggregators(result)
        logging.debug("Trigger function added to manager.")

    def _create_all_ticker(self):
        new_all_ticker = all_ticker(socket_manager=self.bm)
        self.aggregators[ALL_TICKERS_AGGREGATOR] = new_all_ticker
        logging.debug("All ticker created")
        return new_all_ticker

    def _create_aggregator(self, coin_name):
        """Create a new aggregator of a given coin's data."""
        new_aggregator = aggregator(socket_manager=self.bm,
                                    coin_name=coin_name)
        self.aggregators[coin_name] = new_aggregator
        logging.debug("Aggregator for " + coin_name + " created.")
        return new_aggregator

    def get_aggregator(self, coin_name):
        return self.aggregators[coin_name]

    def _tick(self):
        """
        The logic that is performed each time after a
        predetermined delay.
        """
        while self.paused is False:
            self._gatherData()
            self._evaluateTriggers()
            time.sleep(self._tick_freq)

    def _gatherData(self):
        for key in self.aggregators:
            self.aggregators[key].gatherData()

    def _evaluateTriggers(self):
        for trigger in self.triggers:
            result = trigger._evaluate()
            if result is not None:
                trigger._action(result)


class all_ticker(object):
    """
    Starts a web socket that pulls the current
    price of all coins.
    """
    def __init__(self, socket_manager):
        self._bm = socket_manager
        self.ticker_data = []
        self.q = mp.Queue()
        # Start the websocket
        if self._bm:
            self._conn_key = self._bm.start_ticker_socket(callback=self._aggregate_data)

    def _aggregate_data(self, data):
        """ Append the ticker data """
        logging.debug("callback - put data")
        self.q.put(data)

    def gatherData(self):
        """ Pull from the pipe if it's not empty """
        if not(self.q.empty()):
            data = self.q.get()
            # Will to the rescue!!
            self.ticker_data.append(data)
            logging.debug("Gathered data: " + str(data))

    def close_connection(self, data):
        """ Close the connection """
        self._bm.stop_connection(self._conn_key)

    def get_ticker_data(self):
        """ return all the data """
        return self.ticker_data

    def get_price_increase(self, percent, timeframe):
        """
        Returns coins that have increased in price by some
        percent over the given timeframe
        """
        pass


class aggregator(object):
    """
    Aggregates data about a given coin
    through the binance websocket manager.
    """

    def __init__(self, socket_manager, coin_name):
        """Initialize the aggregator class."""
        self._conn_keys = []
        self._bm = socket_manager
        self.coin_name = coin_name
        self._kline_queue = mp.Queue()
        self._depth_queue = mp.Queue()
        self._kline_data = []
        self._depth_data = []
        # Start the websockets and the socket manager
        self._open_kline_websocket()
        self._open_depth_websocket()
        self._bm.start()

    def _open_kline_websocket(self):
        """
        Open the KLine websocket and add the connection to the
        list of open connections.
        """
        conn_key = self._bm.start_kline_socket(self.coin_name,
                                               callback=self._aggregate_kline_data,
                                               interval=KLINE_INTERVAL_5MINUTE)
        self._conn_keys.append(conn_key)

    def _open_depth_websocket(self):
        """
        Open the depth websocket and add the connection to the
        list of open connections.
        """
        conn_key = self._bm.start_depth_socket(self.coin_name,
                                               callback=self._aggregate_depth_data)
        self._conn_keys.append(conn_key)

    """Add the KLine data returned from the websocket to the KLine array"""
    def _aggregate_kline_data(self, data):
        self._kline_queue.put(data)

    """Add the depth data returned from the websocket to the depth array"""
    def _aggregate_depth_data(self, data):
        self._depth_queue.put(data)

    def gatherData(self):
        """ Pull from the pipe if it's not empty """
        if not(self._kline_queue.empty()):
            data = self._kline_queue.get()
            self._kline_data.append(data)
            logging.debug("Gathered kline data: " + data)

        if not(self._depth_queue.empty()):
            data = self._depth_queue.get()
            self._depth_data.append(data)
            logging.debug("Gathered depth data: " + data)

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
                json[field] = data['k'][field]
            result.append(json)
            json = {}
        return result

    def get_prices(self):
        result = []
        prices = self.get_fields_from_kline('c')
        for price in prices:
            result.append(float(price['c']))
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
        for conn_key in self._conn_keys:
            self._bm.stop_connection(conn_key)
        self._conn_keys = []


class trigger(object):
    """
    Base trigger class.

    Implementations override _evaluate(), _action().
    """

    def __init__(self, coin_names, refresh_seconds=1):
        self.coin_names = coin_names
        self.refresh_seconds = refresh_seconds

    def set_aggregators(self, aggregators):
        """Set the aggregators that this trigger function needs to know about.

           Used by the aggregator manager when trigger function is added.
        """
        self._aggregators = aggregators
        logging.debug("Manager set.")

    # Should we take the action?
    def _evaluate(self):
        pass

    # Take the action when _evaluate() returns true
    def _action(self, params):
        pass


class order(trigger):
    """
    Base order class.

    Implementations override _check_place_order(), _get_order_params().
    """

    def __init__(self, coin_names, refresh_seconds=1,
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
        if(self._check_place_order(self.coin_names[0])):
            return {"response": "true tho..."}


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
