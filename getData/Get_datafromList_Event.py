# -*- coding: utf-8 -*-
"""
IB API - Store Historical Data of multiple stocks in dataframe

@author: Mayank Rasu (http://rasuquant.com/wp/)
"""

import os
import threading
import time

import pandas as pd
# Import libraries
from ibapi.client import EClient
from ibapi.contract import Contract
from ibapi.wrapper import EWrapper


class TradeApp(EWrapper, EClient): 
    def __init__(self): 
        EClient.__init__(self, self) 
        self.data = {}
        
    def historicalData(self, reqId, bar):
        if reqId not in self.data:
            self.data[reqId] = [{"Date":bar.date,"Open":bar.open,"High":bar.high,"Low":bar.low,"Close":bar.close,"Volume":bar.volume}]
        else:
            self.data[reqId].append({"Date":bar.date,"Open":bar.open,"High":bar.high,"Low":bar.low,"Close":bar.close,"Volume":bar.volume})
        #  print("reqID:{}, date:{}, open:{}, high:{}, low:{}, close:{}, volume:{}".format(reqId,bar.date,bar.open,bar.high,bar.low,bar.close,bar.volume))

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

###################storing trade app object in dataframe#######################
def dataDataframe(TradeApp_obj, reqId):
    "returns extracted historical data in dataframe format"
    df_data = {}
    isec = 0
    while app.data.__len__() != reqId:
        time.sleep(isleep)
        isec += 1
    print(f"Length of app.data: {app.data.__len__()} waited: {isec} Seconds" )

    df_data = pd.DataFrame(TradeApp_obj.data[reqId])
    df_data.set_index("Date", inplace=True)
    return df_data

def waiter():
    #   print(app.data.__len__())
    isec = 0
    while app.data.__len__() != reqId:
        time.sleep(isleep)
        isec += 1
    print(f"Length of app.data: {app.data.__len__()} waited: {isec} Seconds" )


event = threading.Event()    
app = TradeApp()
app.connect(host='127.0.0.1', port=7497, clientId=23) #port 4002 for ib gateway paper trading/7497 for TWS paper trading
con_thread = threading.Thread(target=websocket_con)
con_thread.start()
time.sleep(1)  # some latency added to ensure that the connection is established
isleep = 1

tickers = {}
xlsx = pd.ExcelFile("..\\input\\Tickers.xlsx")
tickers = pd.read_excel(xlsx, "Tickers", usecols=['StockSymbol'])
print(tickers.head(10))
numtickers = tickers.StockSymbol
print(numtickers)

years = '19 Y'

stockId = 0
reqId = 1
#  tickers = ["FB", "AMZN", "INTC"]
for ticker in numtickers:

    stockId += 1

    if os.path.isdir('..\\output\\' + ticker):
        print(f"This is already processed {ticker} with ID: {stockId}")
        continue

    print(f"This is a new stock {ticker}  reqId {reqId}  with ID: {stockId}")

    histData(reqId, usTechStk(ticker), years, '1 day', 'ADJUSTED_LAST')
    #   waiter()

    print(f"Got Historical Data: {ticker}")
    #extract and store historical data in dataframe
    historicalData_Stock = dataDataframe(app, reqId)
    reqId += 1

    #  STarting OPTION_IMPLIED_VOLATILITY
    histData(reqId, usTechStk(ticker), years, '1 day', 'OPTION_IMPLIED_VOLATILITY')
    #   waiter()

    print(f"Got Impl Volatility Data: {ticker}")
    # extract and store historical data in dataframe
    historicalData_impliedVola = dataDataframe(app, reqId)
    reqId += 1

    #  Starting Historical Vola
    histData(reqId, usTechStk(ticker), years, '1 day', 'HISTORICAL_VOLATILITY')
    #   waiter()

    print(f"Got Historic Volatility Data: {ticker}")
    # extract and store historical data in dataframe
    historicalData_histVola = dataDataframe(app, reqId)
    reqId += 1

    #  Starting Historical Vola
    histData(reqId, usTechStk(ticker), '3 Y', '1 week', 'MIDPOINT')
    #   waiter()

    print(f"Got 3Y price Data: {ticker}")
    # extract and store historical data in dataframe
    historicalData_weekly = dataDataframe(app, reqId)


    os.mkdir('..\\output\\' + ticker)
    with pd.ExcelWriter('..\\output\\' + ticker + '\\Kurse.xlsx') as writer:

        historicalData_Stock.to_excel(writer, sheet_name='Kurse')
        historicalData_impliedVola.to_excel(writer, sheet_name='ImplVola')
        historicalData_histVola.to_excel(writer, sheet_name='HistVola')
        historicalData_weekly.to_excel(writer, sheet_name='Weekly')
    print(f"File: " + '..\\output\\' + ticker + '\\Kurse.xlsx')

    app.data = {}   # Rucksetzen der app.data um Speicher zu sparen
    reqId = 1       # Ruecksetzen der reqId


event.set()

