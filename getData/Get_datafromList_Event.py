# -*- coding: utf-8 -*-
"""
IB API - Store Historical Data of multiple stocks in dataframe

@author: Mayank Rasu (http://rasuquant.com/wp/)
"""

import os
import threading
import time

import pandas as pd
import openpyxl
# Import libraries
from ibapi.client import EClient
from ibapi.contract import Contract
from ibapi.wrapper import EWrapper


class TradeApp(EWrapper, EClient):
    def __init__(self):
        EClient.__init__(self, self)
        self.data = {}

    def error(self, reqId, errorCode, errorString):
        print("Error {} {} {}".format(reqId, errorCode, errorString))
        # os.removedirs('ERROR_200')
        if errorCode == 200:
            # print("Directory", os.getcwd())
            os.mkdir('ERROR_200')

    def contractDetails(self, reqId, contractDetails):
        print("redID: {}, contract:{}".format(reqId, contractDetails.longName))

    def historicalData(self, reqId, bar):
        if reqId not in self.data:
            self.data[reqId] = [
                {"Date": bar.date, "Open": bar.open, "High": bar.high, "Low": bar.low, "Close": bar.close,
                 "Volume": bar.volume}]
        else:
            self.data[reqId].append(
                {"Date": bar.date, "Open": bar.open, "High": bar.high, "Low": bar.low, "Close": bar.close,
                 "Volume": bar.volume})
        #  print("reqID:{}, date:{}, open:{}, high:{}, low:{}, close:{}, volume:{}".format(reqId,bar.date,bar.open,bar.high,bar.low,bar.close,bar.volume))


def usTechStk(symbol, sec_type="STK", currency="USD", exchange="ISLAND"):
    contract = Contract()
    contract.symbol = symbol
    contract.secType = sec_type
    contract.currency = currency
    contract.exchange = exchange
    return contract


def histData(req_num, contract, duration, candle_size, whattoshow):
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
                          chartOptions=[])  # EClient function to request contract details


def websocket_con():
    app.run()
    event.wait()
    if event.is_set():
        print("Event is set")
        app.disconnect()
        # app.close()


###################storing trade app object in dataframe#######################
def dataDataframe(TradeApp_obj, reqId):
    "returns extracted historical data in dataframe format"
    df_data = {}
    waiter(reqId)

    df_data = pd.DataFrame(TradeApp_obj.data[reqId])
    df_data.set_index("Date", inplace=True)
    return df_data


def waiter(reqId):
    #   print(app.data.__len__())
    isec = 0
    while app.data.__len__() != reqId:
        time.sleep(1)
        isec += 1
    print(f"Length of app.data: {app.data.__len__()} waited: {isec} Seconds")


def collect_data(ticker, basedir, sectype, exci, years, stockId):
    reqId = 1
    app.data = {}  # Rucksetzen der app.data um Speicher zu sparen

    if os.path.isdir(basedir + ticker):
        print(f"This is already processed {ticker} with ID: {stockId}")
        return

    print(f"This is a new stock {ticker}  reqId {reqId}  with ID: {stockId}")

    stk = usTechStk(ticker, sectype, exchange=exci)

    #   Check if contract exists

    app.reqContractDetails(100, stk)  # EClient function to request contract details

    # print("***Dir:", os.getcwd())
    time.sleep(5)
    if os.path.isdir('ERROR_200'):
        print(f"No Ticker Data found:  {ticker} with ID: {stockId}")
        # print(os.getcwd())
        os.removedirs('ERROR_200')
        return

    histData(reqId, stk, years, '1 day', 'ADJUSTED_LAST')

    #      print(f"Symbol: {ticker} no data found - wrong Synbol? - Skipped")

    print(f"Got Historical Data: {ticker}")
    # extract and store historical data in dataframe
    historicalData_Stock = dataDataframe(app, reqId)
    reqId += 1

    #  STarting OPTION_IMPLIED_VOLATILITY
    histData(reqId, stk, years, '1 day', 'OPTION_IMPLIED_VOLATILITY')

    print(f"Got Impl Volatility Data: {ticker}")
    # extract and store historical data in dataframe
    historicalData_impliedVola = dataDataframe(app, reqId)
    reqId += 1

    #  Starting Historical Vola
    ierr = histData(reqId, stk, years, '1 day', 'HISTORICAL_VOLATILITY')

    print(f"Got Historic Volatility Data: {ticker}  Error = {ierr}")
    # extract and store historical data in dataframe
    historicalData_histVola = dataDataframe(app, reqId)
    reqId += 1

    #  Starting 3Y period for System
    #   prices adjusted_last
    histData(reqId, stk, '3 Y', '1 week', 'TRADES')

    print(f"Got 3Y price Data: {ticker}")
    # extract and store historical data in dataframe
    historicalData_priceweekly = dataDataframe(app, reqId)
    reqId += 1

    #   implied Volatility
    histData(reqId, stk, '3 Y', '1 week', 'OPTION_IMPLIED_VOLATILITY')

    print(f"Got 3Y implied Volatiity Data: {ticker}")
    # extract and store historical data in dataframe
    historicalData_implvolaweekly = dataDataframe(app, reqId)
    reqId += 1

    #   historic Vola
    histData(reqId, stk, '3 Y', '1 week', 'HISTORICAL_VOLATILITY')

    print(f"Got 3Y historical Volatility  Data: {ticker}")
    # extract and store historical data in dataframe
    historicalData_histvolaweekly = dataDataframe(app, reqId)
    reqId += 1

    os.mkdir(basedir + ticker)
    with pd.ExcelWriter(basedir + ticker + '\\Kurse.xlsx') as writer:
        historicalData_Stock.to_excel(writer, sheet_name='Kurse')
        historicalData_impliedVola.to_excel(writer, sheet_name='ImplVola')
        historicalData_histVola.to_excel(writer, sheet_name='HistVola')
        historicalData_priceweekly.to_excel(writer, sheet_name='Weekly')
        historicalData_implvolaweekly.to_excel(writer, sheet_name='IVWeekly')
        historicalData_histvolaweekly.to_excel(writer, sheet_name='HVWeekly')
    print(f"File: " + basedir + ticker + '\\Kurse.xlsx')


def get_data_from_iab(numtickers, sectype, exchange, basedir='..\\output\\', years='19 Y', ):
    stockId = 0
    #  numtickers = ["FB", "AMZN", "INTC"]

    if not os.path.isdir(basedir):
        os.mkdir(basedir)

    for ticker in numtickers:
        security_type = sectype[stockId]
        exci = exchange[stockId]
        stockId += 1

        collect_data(ticker, basedir, security_type, exci, years, stockId)


select = 0  # 1

tickers = {}
checkticker = 0

inpexel = "..\\input\\Tickers.xlsx"
sheet =  'TickTest'  # 'IVY11'   # 'TickTest'  #   'Index'    'Tickers'  'IVY11'
outdir = '..\\output_Sep24\\'  # '..\\output\\'

if select == 1:  # Funktioniert nicht Besser Excel definierein
    # numtickers = ["VIX", "DJX", "DAX", "RIO", "TLT"]
    # sectype = ["IND", "IND", "IND", "STK", "STK"]
    # exc = ["CBOE", "CBOE", "DTB", "ISLAND", "ISLAND"]
    numtickers = ["TLT"]
    sectype = ["STK"]
    exc = ["ISLAND"]
else:
    xlsx = pd.ExcelFile(inpexel)
    tickers = pd.read_excel(xlsx, sheet_name=sheet, usecols=['StockSymbol', 'Security_Type', 'Exchange'])
    print(tickers.head(10))
    numtickers = tickers.StockSymbol
    sectype = tickers.Security_Type
    exc = tickers.Exchange
    print(numtickers)

event = threading.Event()
app = TradeApp()
app.connect(host='127.0.0.1', port=7497,
            clientId=22)  # port 4002 for ib gateway paper trading/7497 for TWS paper trading
con_thread = threading.Thread(target=websocket_con)
con_thread.start()
time.sleep(1)  # some latency added to ensure that the connection is established

get_data_from_iab(numtickers, sectype, exc, outdir, years='19 Y')

event.set()
