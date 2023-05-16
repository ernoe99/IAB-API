from pathlib import Path

import pandas as pd
import numpy as np
import pandas as pd
import yfinance as yf
from datetime import datetime



def getdata(symb, startdate):
    enddate = datetime.today().strftime('%Y-%m-%d')
    dataidx = yf.download(symb, startdate, enddate)

    csvfile = Path(f'../temp/{symb}.csv')

    dataidx.to_csv(csvfile)

    return dataidx


def calc_monthlydata(dataidx):
    dataidx['month'] = dataidx.index.month
    dataidx['week'] = dataidx.index.isocalendar().week
    dataidx['day'] = dataidx.index.isocalendar().day
    dataidx.rename(columns= {"Adj Close":"Adjclose"}, inplace = True)
    dataidx["Return"] = dataidx.Adjclose.pct_change()
    dataidx["absreturn"] = dataidx.Adjclose.diff()  # Differenz zum Vorgänger (period = 1) ist default.

    idxm = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
    valm = []
    xs = 0.0

    for i in range(1, 13):
        mean = dataidx.loc[(dataidx['month'] == i)].mean(numeric_only=False).Adjclose  # mittlerer Kurs im Monat i
        x = ((1.0 + dataidx.loc[(dataidx['month'] == i)].mean(
            numeric_only=False).absreturn / mean) ** 20.0 - 1.0) * 100  # abs return pro monat in % bezogen auf den mittleren Kurs der Woche
        q = dataidx.loc[(dataidx['month'] == i)].sum().month / float(i)  # Anzahl der Monatseinträge
        valm.append(x)
        print(f"Month: {i} Summe Month: {q}    Summe Return per month:  {x}   ")
        xs += x

    print("***************", xs)

    return idxm, valm


def calc_weekly_data(dataidx):
    sq = 0
    xs = 0
    result = []
    idxw = []
    valw = []

    for i in range(1, 54):
        mean = dataidx.loc[(dataidx['week'] == i)].mean(numeric_only=False).Adjclose  # mittlerer Kurs in der Woche i
        x = ((1.0 + dataidx.loc[(dataidx['week'] == i)].mean(
            numeric_only=False).absreturn / mean) ** 5 - 1.0) * 100.0  # abs return pro woche in % bezogen auf den mittleren Kurs der Woche
        q = dataidx.loc[(dataidx['week'] == i)].sum().week / float(i)  # Anzahl der Wocheneinträge
        # returnperweek = x / q * 100.0
        sq += q
        # xs += dataidx.loc[(dataidx['week'] == i)].mean(numeric_only=False).absreturn
        xs += x
        print(f" Week: {i}  Summe Week: {q} Summe Return per week: {x}   Mean = {mean} ")
        result.append([i, q, x, mean])

        idxw.append(str(i))
        valw.append(x)

    print(xs, sq)

    return idxw, valw


def check_winning_period(idxw, valw, symbol):
    sperf = 0.0
    istart = 0
    res = []
    j = -1 # laufindex geich wie i aber über Jahresende hinaus

    idx = idxw + idxw
    perf = valw + valw

    for iss in idx:
        i = int(iss) - 1
        j += 1
        if j == 51:
            print(j)
        if istart == 0 and j > 53:  # Ende Jahr erreicht und keine Serie detektiert
            break
        if istart == 0:
            if perf[i] > 0.0:  # performance positiv
                istart = int(iss)
                sperf = perf[i]
            else:  # performance negative nächster Versuch
                istart = 0
        else:
            if perf[i] > sperf * -0.1:  # performance positiv oder kleiner 20% des bisherigen Gewinns negativ
                sperf += perf[i]
            else:  # Ende der Gewinnserie
                print(symbol, istart, i, sperf)
                if j - istart >= 2 and sperf > 5.0:  # minimum 3 Wochen erfolgreich und mehr als 5 %
                    res.append([symbol, istart, i, sperf])
                if i - istart < 0:  # geht über das Jahresende hinaus
                    break

                istart = 0
                sperf = 0.0

    return res

def check_loosing_period(idxw, valw, symbol):
    sperf = 0.0
    istart = 0
    res = []
    j = -1  # laufindex

    idx = idxw + idxw
    perf = valw + valw

    for iss in idx:
        i = int(iss) - 1
        j += 1
        if istart == 0 and j > 53:  # Ende Jahr erreicht und keine Serie detektiert
            break
        if istart == 0:
            if perf[i] < 0.0:  # performance negativ
                istart = int(iss)
                sperf = perf[i]
            else:  # performance positiv nächster Versuch
                istart = 0
        else:
            if perf[i] < sperf * -0.1:  # performance negativ oder kleiner 20% des bisherigen Gewinns positiv
                sperf += perf[i]
            else:  # Ende der Gewinnserie
                print(symbol, istart, i, sperf)
                if j - istart >= 2 and sperf < -5.0:  # minimum 3 Wochen erfolgreich und mehr als 5 %
                    res.append([symbol, istart, i, sperf])
                if i - istart < 0:  # geht über das Jahresende hinaus
                    break

                istart = 0
                sperf = 0.0

    return res
