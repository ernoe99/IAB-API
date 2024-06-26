import os
import time
import shutil
from pathlib import Path

import pandas as pd
import numpy as np

from SystemBasicRoutines.pathes_and_constants import target_dir

from SystemBasicRoutines.Basic_VolaWalk import getarrays
from SystemBasicRoutines.makeMatrixFull import makeMatrixFull
from SystemBasicRoutines.blackscholes import getOptionStrike, getOptionMaturity, putvecdays




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

            # df = df.append(df2, ignore_index=True)  # old use concat instead
            df = pd.concat([df, df2])
    print(df)

    gvtotal = df["Win_Loss"].sum()
    print(gvtotal)

    return [gvtotal, df]


def process_VolaWalk(target__dir='..\\output\\', ticker=""):

    if ticker == "":
        liste_directories = list_dir(target__dir)  # Wenn leer, dann alle im Directory
    else:
        liste_directories = [ticker]

    iresult = 0

    for tick in liste_directories:

        # Check if already processed - VolaWalk.xlsx exists
        if Path(target__dir + tick + '\\VolaWalk.xlsx').is_file():
            print(f"{tick}: already processed - skip")
            # continue
        else:
            print(f"Running {tick}")

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
        df_volamatrix = pd.DataFrame(volamatrix, columns=['Volatility', 'shortweek BPerf', 'offset_BP', 'longweek BP',
                                                          'offset BP Long', 'shortweek_BRisk', 'offset short BR',
                                                          'long week BR', 'offfset_lweek BR'])

        with pd.ExcelWriter(target__dir + tick + '\\VolaWalk.xlsx', mode="w") as writer:
            df_volamatrix.to_excel(writer, sheet_name='VolaMatrix'+tick)
            dfbp.to_excel(writer, sheet_name='Best Performance')
            dfbr.to_excel(writer, sheet_name='Best Risk')
            auswertung.to_excel(writer, sheet_name='Auswertung')
        print(f"File: {target__dir}{tick}\\VolaWalk.xlsx")

        dfsymbol = pd.DataFrame([tick], columns=['Symbol'])
        dfres = pd.concat([dfsymbol, auswertung.tail(1)], axis=1)

        if iresult == 0:
            df_result = dfres
            iresult = 1
        else:
            df_result = pd.concat([df_result, dfres])

    print(df_result)

    with pd.ExcelWriter(target_dir + 'Process_Walk_results.xlsx', mode="w") as writer:   # Schreiben der Ergebnisse in Excel
        df_result.to_excel(writer, sheet_name='ProcVolaWalkRes')
    print(f"File: Process_Walk_results.xlsx writen")

    return


# Starting main

# target_dir = '..\\output_Apr23\\'

starttime = time.time()

process_VolaWalk(target_dir, ticker="TLT")  # kein Return Wert ende

print(f"Volawalk finisehd - time: {(time.time() - starttime)} Seconds")

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
