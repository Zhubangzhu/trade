import requests
from time import sleep
from datetime import datetime, time, timedelta
from dateutil import parser


# __________________________

class AstockTrading(object):
    def __init__(self):
        self._open = None
        self._high = None
        self._tick = None

    def getTick(self):
        page = requests.get("http://hq.sinajs.cn/?format=text&list=sh600519")
        stock_info = page.text

        mt_info = stock_info.split(",")

        last = float(mt_info[1])
        trade_datetime = mt_info[30] + ' ' + mt_info[31]

        self._tick = (last, trade_datetime)

    def get_history_data_from_local_machine(self):
        self._open = [1, 2, 3]
        self._high = [2, 3, 4]

    def bar_generator(self, tick):
        pass

    def strategy(self):
        pass

    def buy(self):
        pass

    def sell(self):
        pass

    def runStrategy(self):
        self.getTick()
        self.get_history_data_from_local_machine()
        self.bar_generator()
        self.strategy()


# __________________________________________________
astock = AstockTrading()
astock.getTick()
