import pandas as pd

from getData.makeMatixFull import makeMatrixFull


def getarrays(ticker):

    df = pd.read_excel('..\\output\\' + ticker + '\\Kurse.xlsx', sheet_name='Weekly', index_col=0)
    dfvola = pd.read_excel('..\\output\\' + ticker + '\\Kurse.xlsx', sheet_name='ImplVola', index_col=0)


    dates_df = df.index
    dates = dates_df.to_numpy()

    prices = df.Close.to_numpy()

    implVola = prices.copy()
    i = 0

    for dat in dates_df:

        a = dfvola.loc[dat].Close
        implVola[i] = a
        i += 1

    print("Fertig")
    return [prices, implVola]


# Starting main


ticker = "AAPL"
[prices, implVola] = getarrays(ticker)

startvola = implVola.mean()
if prices[-1] < 70.0:
    intervall = 0.5
else:
    intervall = 2.5

putcall = 1
volamatrix = makeMatrixFull(prices, putcall, ticker)

