import pandas as pd
import yfinance as yf
from datetime import datetime
import matplotlib.pyplot as plt
import pathlib
import waterfall_chart
import plotly.graph_objects as go
import packaging

from Basic_Seasonal import getdata, calc_monthlydata, calc_weekly_data

from tkinter import *



def plot_mdata(idxm, valm):
    mw1 = waterfall_chart.plot(idxm, valm, formatting="{:,.3f}")


def plot_wdata(idxw, valw):
    mw2 = waterfall_chart.plot(idxw, valw, formatting="{:,.4f}")




def waterfallplot(idxm, valm, idxw, valw, symbol, nvals):
    fig = go.Figure(go.Waterfall(
        x=idxm,
        measure=["relative", ] * len(idxm),
        y=valm))
    fig.update_layout(title=f"Monthly data {symbol}", showlegend=True)
    fig.show()

    fig = go.Figure(go.Waterfall(
        x=idxw,
        measure=["relative", ] * len(idxw),
        y=valw))
    fig.update_layout(title=f"Weekly data {symbol}  {nvals} Datensets", showlegend=True)
    fig.show()





def run():
    symbol = symbol_input.get()
    df = getdata(symbol, start)
    [im, vm] = calc_monthlydata(df)
    [iw, vw] = calc_weekly_data(df)
    plot_mdata(im, vm)
    plot_wdata(iw, vw)
    waterfallplot(im, vm, iw, vw, symbol, df.shape[0])


start = "2001-10-01"

window = Tk()
window.title("Seasonal Data Charts")
window.config(padx=40, pady=40)

symbol_input = Entry(width=10)
symbol_input.grid(column=1, row=1)

symbol_label = Label(text="Symbol Yahoo")
symbol_label.grid(column=2, row=1)

c_label = Label(text="Run")
c_label.grid(column=0, row=2)

calculate_button = Button(text="Show", command=run)
calculate_button.grid(column=1, row=2)

mainloop()

print (start)

# symbol = ["BA", "MSFT", "^DJI", "EURUSD=X", "GC=X", "BTC-USD"


# absolute Values


# print(xs, sq)
