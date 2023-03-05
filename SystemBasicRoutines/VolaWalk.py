import os
import shutil

import pandas as pd
import numpy as np

from SystemBasicRoutines.makeMatrixFull import makeMatrixFull
from SystemBasicRoutines.blackscholes import getOptionStrike, getOptionMaturity, putvecdays


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
    dfvola = pd.read_excel(basedir + ticker + '\\Kurse.xlsx', sheet_name='ImplVola', index_col=0)   # TODO umschalten auf historische Volatiliät
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


def VolaWalk(prices, volamatrix, sigma, intervall, bp):
    #  Hier immer eine Woche short und eine Woche long - dann Wechsel
    #  TODO: Ausbau auf 0.3 wochen für S&P und 4 Wochen für dt. Aktien
    #   prices - Wochenschlusskurse
    #   VolaMatrix - in #   Spalten Vola, Strike offset, Saftey Best performance
    #   Safety Best Risk.
    #   sigma - Volatilität in absoluten Werten (nicht Prozent) Dimension wie values
    #   Intervall - Intervall der verfügbaren Optionen

    r = 0.0  # Zins
    t = 7  # Zeit für eine Woche

    for i in np.arange(prices.size - 1):

        [sS, lS] = getOptionStrike(sigma[i], volamatrix, prices[i], bp, intervall)
        [sM, lM] = getOptionMaturity(sigma[i], volamatrix, prices[i], bp, intervall)

        vp = putvecdays(prices[i], 0, sS, r, sigma[i], 7 * sM)[0]
        kp = putvecdays(prices[i], 0, lS, r, sigma[i], 7 * lM)[0]

        # Verkauf Optionen auf der Basis priceB

        evs = putvecdays(prices[i + 1], 0, sS, r, sigma[i + 1], 0)[0]  # Verfall short
        evl = putvecdays(prices[i + 1], 0, lS, r, sigma[i + 1], 7 * (lM - sM))[0]  # value bei Verfall long

        risk = (sS - lS) + (kp - vp)
        gv = (vp - evs) + (evl - kp)

        df2 = pd.DataFrame({"Price": [prices[i]], "Volatility": [sigma[i]], "short Opt strike": [sS],
                            "Short 1964"
                            "Opt price": [vp],
                            "Short Opt end": [evs], "Long Opt strike": [lS], "Long Opt price": [kp],
                            "Long Opt end": [evl], "Win_Loss": [gv], "Vola": [sigma[i + 1]], "Risk": [risk]})

        if i == 0:
            df = df2
            # df = pd.DataFrame({"Price": [prices[i]], "Volatility":[sigma[i]], "short Opt strike":[sS],
            #                    "Short Opt price": [vp],
            #                    "Short Opt end":[evs], "Long Opt strike": [lS], "Long Opt price":[kp],
            #                    "Long Opt end":[evl], "Win/Loss":[gv], "Vola": [sigma[i + 1]], "Risk": [risk]})

        else:
            # df2 = pd.DataFrame({"Price": [prices[i]], "Volatility":[sigma[i]], "short Opt strike":[sS],
            #                    "Short Opt price": [vp],
            #                    "Short Opt end":[evs], "Long Opt strike": [lS], "Long Opt price":[kp],
            #                    "Long Opt end":[evl], "WinLoss":[gv], "Vola": [sigma[i + 1]], "Risk": [risk]})

            df = df.append(df2, ignore_index=True)

    print(df)
    xf = df["Win_Loss"]
    gvtotal = xf.sum()

    print(gvtotal)

    return [gvtotal, df]


def process_VolaWalk(target__dir='..\\output\\', ticker=""):

    if ticker == "":
        liste_directories = list_dir(target__dir)
    else:
        liste_directories = [ticker]

    sresult = []

    for tick in liste_directories:

        #  workdir = target_dir + '\\' + dir
        [prices, implVola] = getarrays(tick, target__dir)

        startvola = implVola.mean()

        if prices[-1] < 70.0:
            intervall = 0.5
        else:
            intervall = 2.5

        putcall = 1
        volamatrix = makeMatrixFull(prices, putcall, ticker)

        [gvtotalbp, dfbp] = VolaWalk(prices, volamatrix, implVola, intervall, 1)
        [gvtotalbr, dfbr] = VolaWalk(prices, volamatrix, implVola, intervall, 2)

        # sort the output for better plotting in Excel and Pandas
        price = dfbp.Price
        volax = dfbp.Volatility * 100.0
        plcum = dfbp.Win_Loss.cumsum()
        plcumbr = dfbr.Win_Loss.cumsum()

        auswertung = pd.concat([price, volax, plcum, plcumbr], axis=1)

        with pd.ExcelWriter(target__dir + tick + '\\VolaWalk.xlsx', mode="w") as writer:
            dfbp.to_excel(writer, sheet_name='Best Performance')
            dfbr.to_excel(writer, sheet_name='Best Risk')
            auswertung.to_excel(writer, sheet_name='Auswertung')
        print(f"File: {target__dir} {tick} \\VolaWalk.xlsx")

        sresult.append(auswertung.last(5))

    with pd.ExcelWriter(tick + '\\Process_Walk_results.xlsx', mode="w") as writer:
        sresult.to_excel(writer, sheet_name='Process VolaWalk Result')
    print(f"File: {tick} \\Process_Walk_results.xlsx writen")

    return sresult


# Starting main

target_dir = '..\\output\\'

s_result = process_VolaWalk(target_dir, ticker="IBKR")


# print(getOptionStrike(0.275, volamatrix, 225.6, 1, 1))
# print(getOptionStrike(0.275, volamatrix, 225.6, 2, 1))
#
# print(getOptionMaturity(0.275, volamatrix, 225.6, 1, 1))
# print(getOptionMaturity(0.275, volamatrix, 225.6, 2, 1))
#

#  os.mkdir('..\\output\\' + ticker)
# ori = '..\\output\\VolaWalk.xlsx'
# targ = '..\\output\\' + ticker
#  stringnam = 'copy ..\\output\\VolaWalk.xlsx ..\\output\\' + ticker

#  os.system('copy ..\\output\\VolaWalk.xlsx ..\\output\\' + ticker)
# shutil.copy(ori, targ)
# in Auswertung muss nur noch ein Diagramm erzeugt werden - alle Kurven werden übereinander dargestellt.

import matplotlib.pyplot as plt
