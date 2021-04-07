# -*- coding: utf-8 -*-
"""
IB API - Store Historical Data of multiple stocks in dataframe

@author: Mayank Rasu (http://rasuquant.com/wp/)
"""

# Import libraries
from ibapi.client import EClient
from ibapi.wrapper import EWrapper
from ibapi.contract import Contract
import pandas as pd
import openpyxl
import threading
import time

class TradeApp(EWrapper, EClient): 
    def __init__(self): 
        EClient.__init__(self, self) 
        self.data = {}
        
    def historicalData(self, reqId, bar):
        if reqId not in self.data:
            self.data[reqId] = [{"Date":bar.date,"Open":bar.open,"High":bar.high,"Low":bar.low,"Close":bar.close,"Volume":bar.volume}]
        else:
            self.data[reqId].append({"Date":bar.date,"Open":bar.open,"High":bar.high,"Low":bar.low,"Close":bar.close,"Volume":bar.volume})
        print("reqID:{}, date:{}, open:{}, high:{}, low:{}, close:{}, volume:{}".format(reqId,bar.date,bar.open,bar.high,bar.low,bar.close,bar.volume))

def usTechStk(symbol,sec_type="STK",currency="USD",exchange="ISLAND"):
    contract = Contract()
    contract.symbol = symbol
    contract.secType = sec_type
    contract.currency = currency
    contract.exchange = exchange
    return contract 

def histData(req_num,contract,duration,candle_size, whattoshow):
    """extracts historical data"""
    app.reqHistoricalData(reqId=req_num, 
                          contract=contract,
                          endDateTime='',
                          durationStr=duration,
                          barSizeSetting=candle_size,
                          whatToShow=whattoshow,
                          useRTH=1,
                          formatDate=1,
                          keepUpToDate=0,
                          chartOptions=[])	 # EClient function to request contract details

def websocket_con():
    app.run()
    event.wait()
    if event.is_set():
        app.close()

event = threading.Event()    
app = TradeApp()
app.connect(host='127.0.0.1', port=7497, clientId=23) #port 4002 for ib gateway paper trading/7497 for TWS paper trading
con_thread = threading.Thread(target=websocket_con)
con_thread.start()
time.sleep(1)  # some latency added to ensure that the connection is established
isleep = 20

tickers = ["FB", "AMZN", "INTC"]
for ticker in tickers:
    histData(tickers.index(ticker),usTechStk(ticker),'15 Y', '1 day', 'ADJUSTED_LAST')
    time.sleep(isleep)

###################storing trade app object in dataframe#######################
def dataDataframe(symbols,TradeApp_obj):
    "returns extracted historical data in dataframe format"
    df_data = {}
    for symbol in symbols:
        df_data[symbol] = pd.DataFrame(TradeApp_obj.data[symbols.index(symbol)])
        df_data[symbol].set_index("Date",inplace=True)
    return df_data

#extract and store historical data in dataframe
historicalData = dataDataframe(tickers,app)

with pd.ExcelWriter('..\\output\Kurse.xlsx') as writer:
    for ticker in tickers:
        historicalData[ticker].to_excel(writer, sheet_name=ticker)

app.data = {}
for ticker in tickers:
    histData(tickers.index(ticker),usTechStk(ticker),'17 Y', '1 day', 'OPTION_IMPLIED_VOLATILITY')
    time.sleep(isleep)
    
#extract and store historical data in dataframe
historicalData = dataDataframe(tickers,app)

with pd.ExcelWriter('..\\output\OptionImplVola.xlsx') as writer:
    for ticker in tickers:
        historicalData[ticker].to_excel(writer, sheet_name=ticker)

app.data = {}
for ticker in tickers:
    histData(tickers.index(ticker),usTechStk(ticker),'19 Y', '1 day', 'HISTORICAL_VOLATILITY')
    time.sleep(isleep)
    
#extract and store historical data in dataframe
historicalData = dataDataframe(tickers,app)

with pd.ExcelWriter('..\\output\HistoricalVola.xlsx') as writer:
    for ticker in tickers:
        historicalData[ticker].to_excel(writer, sheet_name=ticker)

event.set()

