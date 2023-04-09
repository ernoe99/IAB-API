# -*- coding: utf-8 -*-
"""
IBAPI - Bear Spread Strategy (Final) 

@author: Mayank Rasu (http://rasuquant.com/)
"""

from ibapi.client import EClient
from ibapi.wrapper import EWrapper
from ibapi.contract import Contract
from ibapi.contract import ComboLeg
from ibapi.order import Order
import pandas as pd
import numpy as np
import threading
import time
from copy import deepcopy
from datetime import datetime
27
# "RDS A" nach RSX

tickers = ["HL", "T", "VOD", "COP", "TLT", "GLD", "GDX", "ALLO", "CRBU", "CSCO", "VZ", "GSK",
           "VALE", "RIO", "BHP", "EWI", "CRSP", "MO", "PFE", "EWJ", "EMR", "AAPL", "AA", "IBKR",
           "KO", "JNJ", "PHM", "BIIB", "DHI", "PM", "DIA", "GOLD", "SPY", "QQQ", "PSX", "AAL",
           "AZN", "BRK B", "IBM", "TEAM", "RIG",  "INTC", "TSLA", "STM", "MU", "FCX",
           "MMM", "FCEL", "PLUG", "BLDP", "KGC", "GE", "NOK", "EWG", "SLV", "BP", "PSX", "TM",
           "MCD", "MSFT", "CAT", "BA", "PG", "WMT", "DIS", "GFI", "AU", "GM", "F", "GS",
           "MRK", "XOM", "CVX", "QS", "MKFG", "SRAD", "BABA", "EQNR", "AAPL", "AMZN", "MDLZ",
           "SDGR", "GOOGL", "GOOG", "META", "DOW", "TQQQ", "NEM", "PBR", "WHR", "AMGN",
           "VNQ", "VNQI", "BND", "BNDX", "DBE", "DBP", "DBB", "DBA", "EEM", "EFA", "VTI", "XLE", "SHY"]
# "RSX",
# URBAN Jäckle ETFs :"VNQ", "VNQI",   REal Estate US EXus
#                   "BND", "BNDX",  Bonds
#                   "DBE", "DBP", "DBB", "DBA",  Energy (alt,neu XLE) Edelmetalle, Basismetalle, Agrar
#                   "EEM", "EFA","VTI"  Emerging Markets, ex US, US stocks
#                   , "XLE", "SHY"  Energy (US Oelstocks)  cash 1-3 jahres bonds

tickers1 = ["CSCO", "CRBU", "PHM", "VOD", "SPY", "INTC", "RIO", "HL", "GDX", "VALE", "RSX", "QS"]


# [ 12,24, 36, 48, 60, 72
# tickers = ["GOOG","CSCO","INTC","NFLX","MSFT","AAPL","NVDA","TSLA",
#            "SBUX","BGNE","ORLY","MDLZ","MRNA","FB","BIDU","AAL",
#            "ADBE","BYND","AMD","CRVS","LCID","ABCL","PEP","JD","UAL",
#            "HL", "T", "VOD", "COP", "TLT", "GLD", "GDX", "ALLO", "CRBU"]


# Solvemode
#       1 ... Aktien 3 Jahre 1 week  Grosses Depot Langfristig  / Volamatrix Ermittlung
#       2 ... Aktien 1 Jahr  1 day   Grosses Depot Mittelfristig / Optionen check
#       3 ... Optionen quickcheck 60 D / 1 day - BUY SELL Identifikation
#       else    17 Y und 1 week für Saisonalität

class Solvemode():
    def __init__(self, duration, bar_size, end__date=""):
        self.duration = duration
        self.bar_size = bar_size
        self.end_date = end__date
        self.actual_date = datetime.today()


pos_risk = 3000
tot_risk = 20000

Case = 2
end_date = ""

if Case == 1:
    case = Solvemode("3 Y", "1 week", end_date)
elif Case == 2:
    case = Solvemode("1 Y", "1 day", end_date)
elif Case == 3:
    case = Solvemode("60 D", "1 day", end_date)
else:
    case = Solvemode("17 Y", "1 week", end_date)


class TradingApp(EWrapper, EClient):
    def __init__(self):
        EClient.__init__(self, self)
        self.hist_data = {}
        self.hist_data_df = {}
        self.tickers_filtered = []
        self.tickers_filtered_II = []
        self.tickers_filtered_weekLong = []
        self.tickers_filtered_weekShort = []
        self.data = {}
        self.df_data = {}
        self.underlyingPrice = {}
        self.atmCallOptions = {}
        self.otmCallOptions = {}
        self.atr = {}
        self.atr_II = {}
        self.optionPrice = {}
        self.OI = {}
        self.volume = {}
        self.IV = {}
        self.greeks = {}
        self.conID = {}

    def nextValidId(self, orderId):
        super().nextValidId(orderId)
        self.nextValidOrderId = orderId
        print("NextValidId:", orderId)

    #####   wrapper function for reqHistoricalData. this function gives the candle historical data
    def historicalData(self, reqId, bar):
        if reqId not in self.hist_data:
            self.hist_data[reqId] = [
                {"Date": bar.date, "Open": bar.open, "High": bar.high, "Low": bar.low, "Close": bar.close,
                 "Volume": bar.volume}]
        else:
            self.hist_data[reqId].append(
                {"Date": bar.date, "Open": bar.open, "High": bar.high, "Low": bar.low, "Close": bar.close,
                 "Volume": bar.volume})
        print("reqID:{}, date:{}, open:{}, high:{}, low:{}, close:{}, volume:{}".format(reqId, bar.date, bar.open,
                                                                                        bar.high, bar.low, bar.close,
                                                                                        bar.volume))

    #####   wrapper function for reqHistoricalData. this function triggers when historical data extraction is completed
    def historicalDataEnd(self, reqId, start, end):
        super().historicalDataEnd(reqId, start, end)
        print("HistoricalDataEnd. ReqId:", reqId, "from", start, "to", end, " Ticker:", tickers[reqId])
        self.hist_data_df[tickers[reqId]] = pd.DataFrame(self.hist_data[reqId])
        self.hist_data_df[tickers[reqId]].set_index("Date", inplace=True)
        calc_macd(self.hist_data_df[tickers[reqId]])
        calc_rsi(self.hist_data_df[tickers[reqId]])
        calc_atr(self.hist_data_df[tickers[reqId]])
        calc_hist_profit(self.hist_data_df[tickers[reqId]])  # Hier muessen die neuen WErte rein - dann ist es konsequen
        print("Technicals calculated for. ReqId:", reqId)
        ticker_event.set()

    def contractDetails(self, reqId, contractDetails):
        print("extracting data for redID: {}".format(reqId))
        if reqId not in self.data:
            self.data[reqId] = [{"expiry": contractDetails.contract.lastTradeDateOrContractMonth,
                                 "strike": contractDetails.contract.strike,
                                 "call/put": contractDetails.contract.right,
                                 "symbol": contractDetails.contract.localSymbol,
                                 "conid": contractDetails.contract.conId}]
        else:
            self.data[reqId].append({"expiry": contractDetails.contract.lastTradeDateOrContractMonth,
                                     "strike": contractDetails.contract.strike,
                                     "call/put": contractDetails.contract.right,
                                     "symbol": contractDetails.contract.localSymbol,
                                     "conid": contractDetails.contract.conId})

    def contractDetailsEnd(self, reqId):
        super().contractDetailsEnd(reqId)
        print("ContractDetailsEnd. ReqId:", reqId)
        self.df_data[app.tickers_filtered[reqId - 150]] = pd.DataFrame(self.data[reqId])
        contract_event.set()

    def tickPrice(self, reqId, tickType, price, attrib):
        super().tickPrice(reqId, tickType, price, attrib)
        # print("TickPrice. TickerId:", reqId, "tickType:", tickType, "Price:", price)
        if tickType == 4:
            # tickType 4 corresponds to LTP
            if reqId >= 1000 and reqId < 1100:
                self.underlyingPrice[app.tickers_filtered[reqId - 1000]] = price

    def tickSize(self, reqId, tickType, size):
        super().tickSize(reqId, tickType, size)
        # print("TickPrice. TickerId:", reqId, "tickType:", tickType, "Size:", size)
        if reqId >= 1200:
            if (tickType == 27 or tickType == 28) and size != 0:
                self.OI[reqId] = size
            elif tickType == 8:  # 8 is tick type for volume
                self.volume[reqId] = size

    def tickOptionComputation(self, reqId, tickType, impliedVol, delta,
                              optPrice, pvDividend, gamma, vega, theta, undPrice):
        super().tickOptionComputation(reqId, tickType, impliedVol, delta, optPrice, pvDividend,
                                      gamma, vega, theta, undPrice)
        if reqId >= 1100 and reqId < 1200:
            if tickType == 13:
                self.IV[reqId] = impliedVol
                self.optionPrice[reqId] = optPrice
                self.greeks[reqId] = {"Delta": delta, "Gamma": gamma, "Vega": vega, "Theta": theta}


####  this function declares the properties of the instrument. 
def usTechStk(symbol, sec_type="STK", currency="USD", exchange="ISLAND"):
    contract = Contract()
    contract.symbol = symbol
    contract.secType = sec_type
    contract.currency = currency
    contract.exchange = exchange
    return contract


def usTechOpt(symbol, sec_type="OPT", currency="USD", exchange="BOX"):
    contract = Contract()
    contract.symbol = symbol
    contract.secType = sec_type
    contract.currency = currency
    contract.exchange = exchange
    # contract.lastTradeDateOrContractMonth = time.strftime("%Y%m")
    contract.lastTradeDateOrContractMonth = "20210924"
    return contract


def specificOpt(local_symbol, sec_type="OPT", currency="USD", exchange="BOX"):
    contract = Contract()
    contract.symbol = local_symbol.split()[0]
    contract.secType = sec_type
    contract.currency = currency
    contract.exchange = exchange
    contract.right = local_symbol.split()[1][6]
    contract.lastTradeDateOrContractMonth = "20" + local_symbol.split()[1][:6]
    contract.strike = float(local_symbol.split()[1][7:]) / 1000
    return contract


def fetchHistorical(tickers, case: Solvemode):
    for ticker in tickers:
        ticker_event.clear()
        app.reqHistoricalData(reqId=tickers.index(ticker),
                              contract=usTechStk(ticker),
                              endDateTime=case.end_date,
                              durationStr=case.duration,
                              barSizeSetting=case.bar_size,
                              whatToShow='TRADES',  # 'ADJUSTED_LAST'
                              useRTH=1,
                              formatDate=1,
                              keepUpToDate=0,
                              chartOptions=[])
        ticker_event.wait()


def calc_macd(df, a=12, b=26, c=9):
    df["MA_Fast"] = df["Close"].ewm(span=a, min_periods=a).mean()
    df["MA_Slow"] = df["Close"].ewm(span=b, min_periods=b).mean()
    df["MACD"] = df["MA_Fast"] - df["MA_Slow"]
    df["Signal"] = df["MACD"].ewm(span=c, min_periods=c).mean()
    df["BUYSELLMACD"] = df["MACD"] - df[
        "Signal"]  # Buy = positiv, Sell = negativ Werte flachen ab 1. Ableitung positiv starker Trend - eventuelll umgekehrt.
    df["BS_MACD_Dyn"] = (df["BUYSELLMACD"] - df["BUYSELLMACD"].shift()).rolling(5).mean()
    df.drop(["MA_Fast", "MA_Slow"], axis=1, inplace=True)


def calc_rsi(df, n=14):
    df["change"] = df["Close"] - df["Close"].shift(1)
    df["gain"] = np.where(df["change"] >= 0, df["change"], 0)
    df["loss"] = np.where(df["change"] < 0, -1 * df["change"], 0)
    df["avgGain"] = df["gain"].ewm(alpha=1 / n, min_periods=n).mean()
    df["avgLoss"] = df["loss"].ewm(alpha=1 / n, min_periods=n).mean()
    df["rs"] = df["avgGain"] / df["avgLoss"]
    df["rsi"] = 100 - (100 / (1 + df["rs"]))
    df["rsi_norm"] = (df["rsi"] - 50.0) / 100.0  # normalized RSI to fit into diagram
    df.drop(["change", "gain", "loss", "avgGain", "avgLoss", "rs"], axis=1, inplace=True)


def calc_atr(df, n=14):
    "function to calculate True Range and Average True Range"
    df["H-L"] = df["High"] - df["Low"]
    df["H-PC"] = abs(df["High"] - df["Close"].shift(1))
    df["L-PC"] = abs(df["Low"] - df["Close"].shift(1))
    df["TR"] = df[["H-L", "H-PC", "L-PC"]].max(axis=1, skipna=False)
    df["ATR"] = df["TR"].ewm(com=n, min_periods=n).mean()
    df.drop(["H-L", "H-PC", "L-PC", "TR"], axis=1, inplace=True)


def calc_hist_profit(df):
    mean = df["Open"].mean()
    df["Open_norm"] = df["Open"] - mean

    df["Gain"] = df["Open"] - df["Open"].shift()

    s = df["BUYSELLMACD"]
    s = s.mask(s < 0, -1)
    s = s.mask(s > 0, 1)

    df["Sign"] = s
    df["Profit"] = df["Sign"] * df["Gain"]
    df["Profit_cum"] = df["Profit"].cumsum()
    q = df["Profit"].mask(df["Profit"] > 0.005 * mean, 1)  # Profit für Optionen auf 0.5 % setzen = Mittelwert.
    q = q.mask(q < 0, 0)
    df["Profit_OS"] = q

    # Vollständig

    df["buy_sell"] = df["Sign"]
    df["caution"] = 0
    qr = df["BUYSELLMACD"] * df["BS_MACD_Dyn"]
    qr = qr.mask(qr > 0, 0)
    qr = qr.mask(qr < 0, 1)
    df["caution"] = qr  # Caution== 1 / GO AHEAD = 0 Fertig zum Schreiben in Excel


def ticker_filter():  # short
    for ticker in app.hist_data_df:
        macd_recent = app.hist_data_df[ticker]["MACD"].iloc[-1]
        macd_prev = app.hist_data_df[ticker]["MACD"].iloc[-2]
        signal_recent = app.hist_data_df[ticker]["Signal"].iloc[-1]
        signal_prev = app.hist_data_df[ticker]["Signal"].iloc[-2]
        rsi_recent = app.hist_data_df[ticker]["rsi"].iloc[-1]
        if macd_prev > signal_prev and macd_recent < signal_recent and rsi_recent > 50:
            atr = app.hist_data_df[ticker]["ATR"].iloc[-1]
            if 100 * round(atr, 0) <= pos_risk:
                app.tickers_filtered.append(ticker)
                app.atr[ticker] = round(atr + 0.5, 0)


def ticker_filter_day(days):  # short days
    for ticker in app.hist_data_df:
        for iday in range(0, days):
            macd_recent = app.hist_data_df[ticker]["MACD"].iloc[-iday - 1]
            macd_prev = app.hist_data_df[ticker]["MACD"].iloc[-iday - 2]
            signal_recent = app.hist_data_df[ticker]["Signal"].iloc[-iday - 1]
            signal_prev = app.hist_data_df[ticker]["Signal"].iloc[-iday - 2]
            rsi_recent = app.hist_data_df[ticker]["rsi"].iloc[-iday - 1]
            if macd_prev > signal_prev and macd_recent < signal_recent and rsi_recent > 50:
                atr = app.hist_data_df[ticker]["ATR"].iloc[-iday - 1]
                if 100 * round(atr, 0) <= pos_risk:
                    app.tickers_filtered_weekShort.append(ticker)
                    app.atr[ticker] = round(atr + 0.5, 0)
                    break


def ticker_filterII():  # Long
    for ticker in app.hist_data_df:
        macd_recent = app.hist_data_df[ticker]["MACD"].iloc[-1]
        macd_prev = app.hist_data_df[ticker]["MACD"].iloc[-2]
        signal_recent = app.hist_data_df[ticker]["Signal"].iloc[-1]
        signal_prev = app.hist_data_df[ticker]["Signal"].iloc[-2]
        rsi_recent = app.hist_data_df[ticker]["rsi"].iloc[-1]
        if macd_prev < signal_prev and macd_recent > signal_recent and rsi_recent < 50:
            atr = app.hist_data_df[ticker]["ATR"].iloc[-1]
            if 100 * round(atr, 0) <= pos_risk:
                app.tickers_filtered_II.append(ticker)
                app.atr_II[ticker] = round(atr + 0.5, 0)


def ticker_filterII_day(days):  # Lond -days
    for ticker in app.hist_data_df:
        for iday in range(0, days):
            macd_recent = app.hist_data_df[ticker]["MACD"].iloc[-iday - 1]
            macd_prev = app.hist_data_df[ticker]["MACD"].iloc[-iday - 2]
            signal_recent = app.hist_data_df[ticker]["Signal"].iloc[-iday - 1]
            signal_prev = app.hist_data_df[ticker]["Signal"].iloc[-iday - 2]
            rsi_recent = app.hist_data_df[ticker]["rsi"].iloc[-iday - 1]
            if macd_prev < signal_prev and macd_recent > signal_recent and rsi_recent < 50:
                atr = app.hist_data_df[ticker]["ATR"].iloc[-iday - 1]
                if 100 * round(atr, 0) <= pos_risk:
                    app.tickers_filtered_weekLong.append(ticker)
                    app.atr_II[ticker] = round(atr + 0.5, 0)
                    break


def streamSnapshotData(tickers):
    """stream tick leve data"""
    for ticker in tickers:
        app.reqMktData(reqId=1000 + app.tickers_filtered.index(ticker),
                       contract=usTechStk(ticker),
                       genericTickList="",
                       snapshot=False,
                       regulatorySnapshot=False,
                       mktDataOptions=[])
        time.sleep(0.2)


def streamSnapshotGreeksOpt(opt_symbols):
    """stream tick leve data"""
    for opt in opt_symbols:
        app.reqMktData(reqId=1100 + opt_symbols.index(opt),
                       contract=specificOpt(opt),
                       genericTickList="106",
                       snapshot=False,
                       regulatorySnapshot=False,
                       mktDataOptions=[])
        time.sleep(0.2)


def streamSnapshotSizeOpt(opt_symbols):
    """stream tick leve data"""
    for opt in opt_symbols:
        app.reqMktData(reqId=1200 + opt_symbols.index(opt),
                       contract=specificOpt(opt),
                       genericTickList="100, 101, 104, 106, 258",
                       snapshot=False,
                       regulatorySnapshot=False,
                       mktDataOptions=[])
        time.sleep(0.2)


def atm_call_option(contract_df, stock_price):
    temp = contract_df[contract_df["call/put"] == "C"].sort_values(by="expiry", ascending=True)
    temp2 = temp[temp["expiry"] == temp["expiry"].iloc[0]]
    atm_option = temp2.iloc[(temp2["strike"] - stock_price).abs().argsort()[:1]]["symbol"].values[0]
    app.conID[atm_option] = temp2[temp2["symbol"] == atm_option]["conid"].iloc[0]
    return atm_option


def otm_call_option(contract_df, stock_price, atr):
    temp = contract_df[contract_df["call/put"] == "C"].sort_values(by="expiry", ascending=True)
    temp2 = temp[temp["expiry"] == temp["expiry"].iloc[0]]
    otm_option = temp2.iloc[(temp2["strike"] - (stock_price + atr)).abs().argsort()[:1]]["symbol"].values[0]
    app.conID[otm_option] = temp2[temp2["symbol"] == otm_option]["conid"].iloc[0]
    return otm_option


# creating object of the Contract class - will be used as a parameter for other function calls
def comboOptContract(symbol, conID, action, sec_type="BAG", currency="USD", exchange="BOX"):
    contract = Contract()
    contract.symbol = symbol
    contract.secType = sec_type
    contract.currency = currency
    contract.exchange = exchange

    leg1 = ComboLeg()
    leg1.conId = conID[0]
    leg1.ratio = 1
    leg1.action = action[0]
    leg1.exchange = exchange

    leg2 = ComboLeg()
    leg2.conId = conID[1]
    leg2.ratio = 1
    leg2.action = action[1]
    leg2.exchange = exchange

    contract.comboLegs = [leg1, leg2]
    return contract


# creating object of the limit order class - will be used as a parameter for other function calls
def limitOrder(direction, quantity, lmt_price):
    order = Order()
    order.action = direction
    order.orderType = "LMT"
    order.totalQuantity = quantity
    order.lmtPrice = lmt_price
    return order


##### function to establish the websocket connection to TWS
def connection():
    app.run()


app = TradingApp()
app.connect(host='127.0.0.1', port=7497,
            clientId=23)  # port 4002 for ib gateway paper trading/7497 for TWS paper trading

ConThread = threading.Thread(target=connection)
ConThread.start()

ticker_event = threading.Event()
contract_event = threading.Event()

fetchHistorical(tickers, case)
ticker_filter()
ticker_filterII()
print("Short Tickers: ", app.tickers_filtered)
print("Long Tickers: ", app.tickers_filtered_II)

ticker_filter_day(5)
ticker_filterII_day(5)

print("Short Tickers: ", app.tickers_filtered_weekShort)
print("Long Tickers: ", app.tickers_filtered_weekLong)


def ticker_actual():
    idx = 0
    result = {}
    result2 = {}
    t = {}
    res_df = {}
    q_df = {}

    for ticker in app.hist_data_df:

        df = deepcopy(app.hist_data_df[ticker])  # ticker Daten

        if df["BUYSELLMACD"].iloc[-1] > 0:
            trend = "BUY"
        else:
            trend = "SELL"

        macd = df["BUYSELLMACD"].iloc[-1]
        dyn_macd = df["BS_MACD_Dyn"].iloc[-1]

        if df["BUYSELLMACD"].iloc[-1] * df["BS_MACD_Dyn"].iloc[-1] < 0:
            caution = "CAUTION"
        else:
            caution = "GO AHEAD"

        summe = df["Profit"].sum()
        q = df["Profit_OS"]  # nur 1 bei richtiger Richtung > 0.005 * mean
        hr = q.sum() / q.value_counts().sum()  # Hitrate
        mean = df["Open"].mean()

        print(f"{ticker}: {trend} with {caution}  MACD: {macd}   Dyn. MACD: {dyn_macd} MeanPrice {mean}")
        print(f"Total expected Profit:  {summe} Percent {summe / mean} Expected Hitrate - daily base:  {hr}")

        df.to_excel("..\\output\\" + ticker + "_" + str(Case) + ".xlsx")

        result[ticker] = {"BuySell": trend, "Caution": caution, "MACD": macd, "DynMACD": dyn_macd, "Profit": summe,
                          "Profit_pct": summe / mean * 100.0, "Hitrate": hr}

        for i in (5, 4, 3, 2, 1):
            if df["BUYSELLMACD"].iloc[-i] > 0:
                t[i] = "BUY"
            else:
                t[i] = "SELL"

            macd = df["BUYSELLMACD"].iloc[-i]
            dyn_macd = df["BS_MACD_Dyn"].iloc[-i]

            if df["BUYSELLMACD"].iloc[-i] * df["BS_MACD_Dyn"].iloc[-i] < 0:
                t[i] = t[i] + "C"
            else:
                t[i] = t[i] + "GO"

        result2[ticker] = {"BuySell": trend, "Caution": caution, "MACD": macd, "DynMACD": dyn_macd, "Profit": summe,
                           "Profit_pct": summe / mean * 100.0, "Hitrate": hr, "BS5": t[5], "BS4": t[4], "BS3": t[3],
                           "BS2": t[2], "BS1": t[1]}

    res_df = pd.DataFrame(result).transpose()
    res_df.to_excel("..\\Result\\" + "Result.xlsx")
    res_df = pd.DataFrame(result2).transpose()
    res_df.to_excel("..\\Result\\" + "Result2.xlsx")


ticker_actual()

#
# #streaming underlying price on a separate thread
# streamThread = threading.Thread(target=streamSnapshotData, args=(app.tickers_filtered,))
# streamThread.start()
# time.sleep(10) #some lag added to ensure that streaming has started
#
# for ticker in app.tickers_filtered:
#     contract_event.clear() #clear the set flag for the event object
#     app.reqContractDetails(150+app.tickers_filtered.index(ticker), usTechOpt(ticker)) # EClient function to request contract details
#     contract_event.wait() #waiting for the set flag of the event object
#     app.atmCallOptions[ticker] = atm_call_option(app.df_data[ticker],app.underlyingPrice[ticker])
#     app.otmCallOptions[ticker] = otm_call_option(app.df_data[ticker],app.underlyingPrice[ticker],app.atr[ticker])
#
# #storing selected option contracts in a list
# options = list(app.atmCallOptions.values()) + list(app.otmCallOptions.values())
#
# #streaming option contracts' current price on a separate thread
# optGreeksStreamThread = threading.Thread(target=streamSnapshotGreeksOpt, args=(options,))
# optGreeksStreamThread.start()
# #time.sleep(10) #some lag added to ensure that streaming has started
#
# optSizeStreamThread = threading.Thread(target=streamSnapshotSizeOpt, args=(options,))
# optSizeStreamThread.start()
# time.sleep(15) #some lag added to ensure that streaming has started
#
# def optMarketData(symbol,ATM=True):
#     strikes = []
#     index = []
#     for opt in options:
#         if opt.split()[0]==symbol:
#             strikes.append(float(opt.split()[1][7:])/1000)
#             index.append(options.index(opt))
#
#     if ATM:
#         return_index = index[strikes.index(min(strikes))]
#         strike = min(strikes)
#     else:
#         return_index = index[strikes.index(max(strikes))]
#         strike = max(strikes)
#
#     return {"LTP":app.optionPrice[1100+return_index],
#             "Greeks":app.greeks[1100+return_index],
#             "OI":app.OI[1200+return_index],
#             "Volume":app.volume[1200+return_index],
#             "ConID":app.conID[options[return_index]],
#             "Strike":strike}
#
#
# def stackRanking():
#     rr_ratio = []
#
#     for ticker in app.tickers_filtered:
#         payoff = (optMarketData(ticker,True)["LTP"] - optMarketData(ticker,False)["LTP"])*100
#         risk = (optMarketData(ticker,False)["Strike"] - optMarketData(ticker,True)["Strike"])*100
#         rr_ratio.append(round(payoff/risk,2))
#         print("risk reward ratio for {} = {}".format(ticker, round(payoff/risk,2)))
#
#     return [app.tickers_filtered[rr_ratio.index(x)] for x in sorted(rr_ratio)]
#
# def place_combo_order_bearspread(symbol,quantity):
#     order_id = app.nextValidOrderId
#     conIDs = [optMarketData(symbol,True)["ConID"],optMarketData(symbol,False)["ConID"]]
#     limit_price = round(optMarketData(symbol,False)["LTP"] - optMarketData(symbol,True)["LTP"],2)
#     app.placeOrder(order_id,comboOptContract(symbol,conIDs,["SELL","BUY"]),limitOrder("BUY",quantity,limit_price)) # EClient function to request contract details
#     time.sleep(2) # some latency added to ensure that the contract details request has been processed
#
#
# ranked_tickers = stackRanking()[:int(tot_risk/pos_risk)]
#
# # for ticker in ranked_tickers:
# #     quantity = max(1,round(pos_risk/((optMarketData(ticker,False)["Strike"]-optMarketData(ticker,True)["Strike"])*100),0))
# #     place_combo_order_bearspread(ticker,quantity)
# #     app.reqIds(-1)
# #     time.sleep(2)
