from ibapi.client import EClient
from ibapi.wrapper import EWrapper
from ibapi.contract import Contract

import threading
import time
import pandas as pd
import datetime
from datetime import datetime

class IBapi(EWrapper, EClient):
    def __init__(self):
        EClient.__init__(self, self)
        self.data = [] #Initialize variable to store candle

        self.symbol = ''
        
    def tickByTickBidAsk(self, reqId, time, bidPrice, askPrice, bidSize, askSize, tickAttribBidAsk):
        bidAsk = {
                "BidPrice": bidPrice,
                "BidSize": bidSize,
                "AskPrice": askPrice,
                "AskSize": askSize
            }
        self.data.append(bidAsk)

        df = pd.DataFrame.from_dict(self.data)
        if len(self.data) > 3:
            self.data = []
            print("******************* PULL OrderBook ********************")
            df.to_csv(f"harvesting_ib/csv/{self.symbol}_orderbook.csv", index=False)

def run_loop():
	app.run()

if __name__ == '__main__':
    app = IBapi()
    app.connect('127.0.0.1', 4002, 123)

    ticker = 'TSLA'
    app.symbol = 'TSLA'

    #Start the socket in a thread
    api_thread = threading.Thread(target=run_loop, daemon=True)
    api_thread.start()

    time.sleep(1) #Sleep interval to allow time for connection to server

    #Create contract object
    apple_contract = Contract()
    apple_contract.symbol = ticker
    apple_contract.secType = 'STK'
    apple_contract.exchange = 'SMART'
    apple_contract.currency = 'USD'


    app.reqTickByTickData(1, apple_contract, "BidAsk", 0, True)

    # time.sleep(10) #Sleep interval to allow time for incoming price data
    # app.disconnect()