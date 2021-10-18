from time import sleep
from datetime import datetime, time, timedelta
from dateutil import parser
import requests

def getTick():
    page = requests.get("http://hq.sinajs.cn/?format=text&list=sh600519")
    stock_info = page.text

    mt_info = stock_info.split(",")

    last = float(mt_info[1])
    trade_datetime = mt_info[30] + ' ' + mt_info[31]

    return (last, trade_datetime)
trade_time = time(9, 30)
while time(9) < trade_time < time(15):
    last_tick = getTick()
    print(last_tick)
    trade_time = parser.parse(last_tick[1]).time()
    sleep(1)