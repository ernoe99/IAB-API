import os.path

import pandas as pd

tickers = {}
xlsx = pd.ExcelFile("..\\input\\Tickers.xlsx")
tickers = pd.read_excel(xlsx, "Tickers", usecols=['StockSymbol'])
print(tickers.head(10))
numtickers = tickers.StockSymbol
print(numtickers)


reqId = 1
#  tickers = ["FB", "AMZN", "INTC"]
for ticker in numtickers:
    print(ticker)

    if os.path.isdir('..\\output\\' + ticker):
        print(f"This is a directory  {ticker}")
        continue
    else:
        print(f"This is not a directory {ticker}  reqId {reqId} \n")
        reqId += 1

