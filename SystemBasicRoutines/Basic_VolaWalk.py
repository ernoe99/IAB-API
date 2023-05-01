from pathlib import Path
import pandas as pd
import os


def list_dir(dire):

    liste = []
    i = 0
    for root, dirs, files in os.walk(dire):
        for name in dirs:
            liste.append(name)
            #  print(name)
            i += 1
    return liste


def getarrays(ticker, basedir='..\\output\\'):
    df = pd.read_excel(basedir + ticker + '\\Kurse.xlsx', sheet_name='Weekly', index_col=0)
    dfvola = pd.read_excel(basedir + ticker + '\\Kurse.xlsx', sheet_name='IVWeekly', index_col=0)   # Changed to IVWeekly - TODO umschalten auf historische Volatiliät
    # dates_df = df.index
    # dates = dates_df.to_numpy()

    # prices = df.Close.to_numpy()

    # implVola = prices.copy()
    # i = 0

    # Alternative

    print("Fertig")

    dfnew = df.merge(dfvola, how='inner', left_index=True, right_index=True)

    implVola = dfnew.Close_y.to_numpy()
    prices = dfnew.Close_x.to_numpy()

    return [prices, implVola]
