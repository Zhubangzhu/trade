import os
from time import sleep
from datetime import datetime, time, timedelta
from dateutil import parser
import requests
import pandas as pd
import numpy as np


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
        self._is_new_bar = None
        self._ma20 = None
        self._current_orders = {}
        self._history_orders = {}
        self._order_number = 0
        self._init = False

    def getTick(self):
        page = requests.get("http://hq.sinajs.cn/?format=text&list=sh600519")
        stock_info = page.text
        mt_info = stock_info.split(",")
        last = float(mt_info[1])
        trade_datetime = mt_info[30] + ' ' + mt_info[31]
        # 2020/12/10 9:25 ->
        if trade_datetime.time() < time(9, 30):
            trade_time = datetime.combine(trade_datetime.date(), time(9, 30))

        self._tick = (trade_datetime, last)

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
            self._close.insert(0, self._tick[1])
            self._dt.insert(0, self._tick[0])
            self._is_new_bar = True
        else:
            self._high[0] = max(self._high[0], self._tick[1])
            self._low[0] = min(self._low[0], self._tick[1])
            self._close[0] = self._tick[1]
            self._dt[0] = self._tick[0]
            self._is_new_bar = False

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
        self._current_orders[key]["pnl"] = (price - self._current_orders[key]['open_price']) * \
                                           self._current_orders[key]["volume"] \
                                           - price * self._current_orders[key]["volume"] * 1 / 1000 \
                                           - (price + self._current_orders[key]['open_price']) * 3 / 10000
        self._history_orders[key] = self._current_orders.pop(key)

    def strategy(self):
        if self._is_new_bar:
            sum_ = 0
            for item in self._close[1:21]:
                sum_ = sum_ + item
            self._ma20 = sum_ / 20

        if 0 == len(self._current_orders):
            if self._close[0] < 0.97 * self._ma20:
                volume = int((100000 / self._close[0]) / 100) * 100
                price = self._close[0]
                self.buy(price + 0.01, volume)
        elif 1 == len(self._current_orders):
            if self._close[0] > 1.03 * self._ma20:
                key = list(self._current_orders.keys())[0]
                self.sell(key, self._close[0] - 0.01)
        else:
            raise ValueError("we have more than 1 order")

    def bar_generator_for_backTesting(self, tick):
        last_bar_start_minute = None
        if tick[0].minute % 5 == 0 and tick[0].minute != self._last_bar_start_minute:
            self._last_bar_start_minute = tick[0].minute
            self._open.insert(0, tick[1])
            self._high.insert(0, tick[1])
            self._low.insert(0, tick[1])
            self._close.insert(0, tick[1])
            self._dt.insert(0, tick[0])
            self._is_new_bar = True
        else:
            self._high[0] = max(self._high[0], tick[1])
            self._low[0] = min(self._low[0], tick[1])
            self._close[0] = tick[1]
            self._dt[0] = tick[0]
            self._is_new_bar = False

    def run_backTesting(self, ticks):
        for tick in ticks:
            self.bar_generator_for_backTesting(tick)
            if self._init:
                self.strategy()
            else:
                if len(self._open) >= 100:
                    self._init = True
                    self.strategy()


# ---------------------------------------------------

ma = AstockTrading("ma")
ma.get_history_data_from_local_machine()

while time(9, 26) < datetime.now().time() < time(11, 32) or \
        time(13) < datetime.now().time() < time(15):
    ma.getTick()
    ma.bar_generator()


def get_ticks_for_backTesting():
    tick_path = "600036_data/600036_ticks.csv"
    bar_path = "600036_data/600036_5m.csv"
    if os.path.exists(tick_path):
        ticks = pd.read_csv(
            tick_path,
            parse_dates=["datetime"],
            index_col="datetime"
        )
        tick_list = []
        for index, row in ticks.iterrows():
            tick_list.append((index, row[0]))
        ticks = np.array(tick_list)
    else:
        bar_5m = pd.read_csv(bar_path)
        bar_5m.head(5)
        ticks = []
        for index, row in bar_5m.iterrows():
            if row['open'] < 30:
                step = 0.01
            elif row['open'] < 60:
                step = 0.03
            elif row['open'] < 90:
                step = 0.05
            else:
                step = 0.1
            arr = np.arange(row['open'], row['high'], step)
            arr = np.append(arr, row['high'])
            arr = np.append(arr, np.arange(row['open'] - step, row['low'], -step))
            arr = np.append(arr, row['low'])
            arr = np.append(arr, row['close'])

            i = 0
            for item in arr:
                dt = parser.parse(row['datetime']) - timedelta(minutes=5)
                ticks.append((dt + timedelta(seconds=0.1 * i), item))
                i += 1
        ticks_df = pd.DataFrame(ticks, columns=["datetime", 'price'])
        ticks_df = pd.DataFrame(ticks, columns=["datetime", 'price'])
        ticks_df.to_csv(tick_path, index=0)
    return ticks


if __name__ == '__main__':
    ticks = get_ticks_for_backTesting()
    ast = AstockTrading('ma')
    ast.run_backTesting(ticks)
    print(ast._current_orders)
    print(ast._history_orders)
    result = 0
    for item in ast._history_orders.values():
        result+=item["pnl"]
    print(result)