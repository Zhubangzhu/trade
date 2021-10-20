from time import sleep
from datetime import datetime, time, timedelta
from dateutil import parser
import requests


def getTick():



def get_history_data_from_local_machine():
    return dt, open, high, low, close, volume


# how to save and import history data
def bar_generator(tick, dt, open, high, low, close, volume):
    # last < 0.95 * ma20, long, last > ma20 * 1.05, sell
    # 1. update 5 minute ma20 , not daily data
    # 2. compare last and ma20 -> buy or sell or pass
    # assume we have history data, open, high, low ,close, dt
    last_bar_start_minute = None
    if tick[0].minute % 5 == 0 and tick[0].minute != last_bar_start_minute:
        last_bar_start_minute = tick[0].minute
        open.insert(0, tick[1])
        high.insert(0, tick[1])
        low.insert(0, tick[1])
        close.insert(0, tick[1])
        dt.insert(0, tick[0])
    else:
        high[0] = max(high[0], tick[1])
        low[0] = min(low[0], tick[1])
        close[0] = tick[1]
        dt[0] = tick[0]
    return dt, open, high, low, close, volume

def buy():
    pass
def sell():
    pass
def strategy(dt, open, high, low, close, volume):
    sum_ = 0
    for item in close[1:21]:
        sum_ = sum_ + item
    ma20 = sum_ / 20

    if close[0] < 0.95 * ma20:
        buy()
    elif close[0] > 1.05 * ma20:
        if I have a long postion:
            sell()
        else:
            pass
    else:
        pass


# ---------------------------------------------------
dt, open, high, low, close, volume = get_history_data_from_local_machine()
trade_time = time(9,30)
while time(9) < trade_time < time(15):
    last_tick = getTick()
    dt, open, high, low, close, volume = bar_generator(last_tick, dt, open, high, low, close, volume)
    strategy(dt, open, high, low, close, volume)
    trade_time = parser.parse(last_tick[1]).time()
    sleep(1)

