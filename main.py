from time import sleep
from datetime import datetime, time, timedelta
from dateutil import parser
import requests


class AstockTrading(object):
    def __init__(self, strategy_name):
        self._strategy_name = strategy_name
        self._open = []
        self._high = []
        self._low = []
        self._close = []
        self._dt = []
        self._tick = []
        self._last_bar_start_minute = None
        self._isNewBar = None
        self._ma20 = None
        self._current_orders = {}
        self._history_orders = {}
        self._order_number = 0

    def getTick(self):
        page = requests.get("http://hq.sinajs.cn/?format=text&list=sh600519")
        stock_info = page.text
        mt_info = stock_info.split(",")
        last = float(mt_info[1])
        trade_datetime = mt_info[30] + ' ' + mt_info[31]
        # 2020/12/10 9:25 ->
        if trade_datetime.time() < time(9, 30):
            trade_time = datetime.combine(trade_datetime.date(), time(9, 30))

        self._tick = (last, trade_datetime)

    def get_history_data_from_local_machine(self):
        self._open = []
        self._high = []
        self._low = []
        self._close = []
        self._dt = []

    def bar_generator(self):
        last_bar_start_minute = None
        if self._tick[0].minute % 5 == 0 and self._tick[0].minute != self._last_bar_start_minute:
            self._last_bar_start_minute = self._tick[0].minute
            self._open.insert(0, self._tick[1])
            self._high.insert(0, self._tick[1])
            self._low.insert(0, self._tick[1])
            self._.insert(0, self._tick[1])
            self._dt.insert(0, self._tick[0])
            self.isNewBar = True
        else:
            self._high[0] = max(self._high[0], self._tick[1])
            self._low[0] = min(self._low[0], self._tick[1])
            self._close[0] = self._tick[1]
            self._dt[0] = self._tick[0]
            self._isNewBar = False

    def buy(self, price, volume):
        self._order_number += 1
        key = "order" + str(self._order_number)
        self._current_orders[key] = {
            "open_datetime": self._dt[0],
            "open_price": price,
            "volume": volume
        }

    def sell(self, key, price):
        self._current_orders[key]["close_price"] = price
        self._current_orders[key]["close_datetime"] = self._dt[0]
        self._history_orders[key] = self._current_orders.pop(key)

    def strategy(self):
        if self._isNewBar:
            sum_ = 0
            for item in self._close[1:21]:
                sum_ = sum_ + item
            self._ma20 = sum_ / 20

        if 0 == len(self._current_orders):
            if self._close[0] < 0.95 * self._ma20:
                volume = int((100000 / self._close[0]) / 100) * 100
                price = self._close[0]
                self.buy(price + 0.01, volume)
        elif 1 == len(self._current_orders):
            if self._close[0] > 1.05 * self._ma20:
                self._current_orders.items()
                self.sell()
        else:
            raise ValueError("we have more than 1 order")


# ---------------------------------------------------

ma = AstockTrading("ma")
ma.get_history_data_from_local_machine()

while time(9, 26) < datetime.now().time() < time(11, 32) or \
        time(13) < datetime.now().time() < time(15):
    ma.getTick()
    ma.bar_generator()
