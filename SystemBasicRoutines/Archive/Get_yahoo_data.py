import pandas as pd
import yfinance as yf
from datetime import datetime
import matplotlib.pyplot as plt
import pathlib
import waterfall_chart

from tkinter import *

def getdata(symb, startdate):

    enddate = datetime.today().strftime('%Y-%m-%d')
    dataidx = yf.download(symb, startdate, enddate)

    csvfile = pathlib.Path(f'../temp/{symb}.csv')

    dataidx.to_csv(csvfile)

    return dataidx

def calc_monthlydata (df):


start = "2001-10-01"



enddate = datetime.today().strftime('%Y-%m-%d')

window = Tk()
symbol = "HL"

# symbol = ["BA", "MSFT", "^DJI", "EURUSD=X", "GC=X", "BTC-USD"

dataidx = yf.download(symbol, start, enddate)

csvfile = pathlib.Path(f'../../temp/{symbol}.csv')

dataidx.to_csv(csvfile)

dataidx['month'] = dataidx.index.month
dataidx['week'] = dataidx.index.isocalendar().week
dataidx['day'] = dataidx.index.isocalendar().day

dataidx["Return"] = dataidx.Close.pct_change()
dataidx["absreturn"] = dataidx.Close.diff()  # Differenz zum Vorgänger (period = 1) ist default.

# absolute Values
idxm = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
valm = []
xs = 0.0

for i in range(1, 13):
    mean = dataidx.loc[(dataidx['month'] == i)].mean(numeric_only=False).Close  # mittlerer Kurs im Monat i
    x = ((1.0 + dataidx.loc[(dataidx['month'] == i)].mean(
        numeric_only=False).absreturn / mean) ** 20.0 - 1.0) * 100  # abs return pro monat in % bezogen auf den mittleren Kurs der Woche
    q = dataidx.loc[(dataidx['month'] == i)].sum().month / float(i)  # Anzahl der Monatseinträge
    valm.append(x)
    print(f"Month: {i} Summe Month: {q}    Summe Return per month:  {x}   ")
    xs += x

print("***************", xs)

mw1 = waterfall_chart.plot(idxm, valm, formatting="{:,.3f}")

sq = 0
xs = 0
result = []
idxw = []
valw = []

for i in range(1, 54):  # TODO: Hier ist noch ein Fehler im Vergleich zum Excel.
    mean = dataidx.loc[(dataidx['week'] == i)].mean(numeric_only=False).Close  # mittlerer Kurs in der Woche i
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

mw2 = waterfall_chart.plot(idxw, valw, formatting="{:,.4f}")

print(xs, sq)

