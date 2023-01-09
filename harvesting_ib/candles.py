# Responsible for pulling data from IBKR
# Saving it to down to sqllite file.

from websockets import connect
import asyncio
import sys
import sqlite3
import aiosqlite
import json
import time
from datetime import datetime


from ib_insync import *
from IPython.display import display, clear_output
import pandas as pd

ib = IB()
ib.connect('127.0.0.1', 4002, clientId=1)
symbol = 'TSLA'


def save_down(contract):
    while True:
        df = getHistoricalData(contract)
        # print(df)
        if df is not None:
            print("******************* PULL Candles ********************")
            df.to_csv(f"harvesting_ib/csv/{symbol}_candles.csv", index=False)
        time.sleep(10)


def getHistoricalData(contract):
    bars = ib.reqHistoricalData(
        contract,
        endDateTime='',
        durationStr='900 S',
        barSizeSetting='1 secs',
        whatToShow='TRADES',
        useRTH=False,
        formatDate=1)

    df = util.df(bars)
    return df


if __name__ == '__main__':
    contract = Stock(symbol, 'SMART', 'USD')
    save_down(contract)