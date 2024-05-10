import os
import time
import shutil
from pathlib import Path

import pandas as pd
import numpy as np

from Basic_VolaWalk import list_dir
from Basic_Seasonal import calc_weekly_data, calc_monthlydata
from Basic_Seasonal import getdata, check_winning_period, check_loosing_period

def plot_mdata(idxm, valm):
    mw1 = waterfall_chart.plot(idxm, valm, formatting="{:,.3f}")


def plot_wdata(idxw, valw):
    mw2 = waterfall_chart.plot(idxw, valw, formatting="{:,.4f}")


def waterfallplot(idxm, valm, idxw, valw, symbol, nvals):

    fig = go.Figure(go.Waterfall(
        x=idxm,
        measure=["relative",]*len(idxm),
        y=valm))
    fig.update_layout(title=f"Monthly data {symbol}", showlegend=True)
    fig.show()

    fig = go.Figure(go.Waterfall(
        x=idxw,
        measure=["relative",]*len(idxw),
        y=valw))
    fig.update_layout(title=f"Weekly data {symbol}  {nvals} Datensets", showlegend=True)
    fig.show()

def build_seasonal_db(target__dir='..\\output\\', ticker=""):

    if ticker == "":
        liste_directories = list_dir(target__dir)  # Wenn leer, dann alle im Directory
    else:
        liste_directories = [ticker]


    iresult = 0

    result_winning = []
    result_loosing = []

    for symbol in liste_directories:

        df = getdata(symbol, start)
        [im, vm] = calc_monthlydata(df)  # zum Besetzen der Wochen und Monatsdaten
        [iw, vw] = calc_weekly_data(df)
        resw = check_winning_period(iw, vw, symbol)
        resl = check_loosing_period(iw, vw, symbol)
        print(resw)
        print(resl)

        result_winning += resw
        result_loosing += resl

    colnam = ['Symbol', 'Startweek', 'Endweek', 'Performance']
    df_result_w = pd.DataFrame(result_winning, columns=colnam)
    df_result_l = pd.DataFrame(result_loosing, columns=colnam)



    with pd.ExcelWriter(target__dir + '\\SeasonalCheck.xlsx') as writer:
        df_result_w.to_excel(writer, sheet_name='Upside')
        df_result_l.to_excel(writer, sheet_name='Downside')

    print(f"File: " + target__dir + '\\SeasonalCheck.xlsx')






# Starting main

target_dir = '..\\output_Apr23\\'

start = "2001-10-01"
starttime = time.time()

ticker = "MMM"

build_seasonal_db(target_dir, ticker="")  # kein Return Wert ende
# build_seasonal_db(target_dir, ticker=ticker)  # kein Return Wert ende

print(f"Sesonal Database finisehd - time: {(time.time() - starttime)} Seconds")



