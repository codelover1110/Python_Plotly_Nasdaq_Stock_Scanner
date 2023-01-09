from ib_insync import *
from IPython.display import display, clear_output
import pandas as pd
import asyncio
import time
import asyncio

ib = IB()
ib.connect('127.0.0.1', 4002, clientId=16, timeout=0)

def save_orderbook(symbol):
    contract = Stock(symbol, 'SMART', 'USD')
    # contracts = ib.qualifyContracts(contract)
    # ib.qualifyContracts(contract)
    ticker = ib.reqMktDepth(contract)

    df = pd.DataFrame(index=range(5),
            columns='bidSize bidPrice askPrice askSize'.split())

    def onTickerUpdate(ticker):
        bids = ticker.domBids
        for i in range(5):
            df.iloc[i, 0] = bids[i].size if i < len(bids) else 0
            df.iloc[i, 1] = bids[i].price if i < len(bids) else 0
        asks = ticker.domAsks
        for i in range(5):
            df.iloc[i, 2] = asks[i].price if i < len(asks) else 0
            df.iloc[i, 3] = asks[i].size if i < len(asks) else 0
        # clear_output(wait=True)
        print(df)
        df.to_csv(f"csv/{symbol}_orderbook.csv", index=False)

    ticker.updateEvent += onTickerUpdate

    IB.sleep(60*3)



if __name__ == '__main__':
    symbol = 'AAPL'
    save_orderbook(symbol)