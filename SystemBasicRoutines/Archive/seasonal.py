import pandas as pd
import os

print(os.getcwd())

odir = '..\\output_test\\'

stock = "GDX"

data = pd.read_excel(f'{odir}{stock}\\Kurse.xlsx')

data["datetime"] = data.Date.apply(lambda x: pd.to_datetime(str(x)))

dataidx = data.set_index(data.datetime).drop("Date", axis = 1)

dataidx['month'] = dataidx['datetime'].dt.month
dataidx['week'] = dataidx['datetime'].dt.isocalendar().week
dataidx['day'] = dataidx['datetime'].dt.isocalendar().day


dataidx["Return"] = dataidx.Close.pct_change()
dataidx["absreturn"] = dataidx.Close.diff()  # Differenz zum Vorgänger (period = 1) ist default.

dataidx
df2 = dataidx.groupby(['month'])
df2

for i in range(1, 13):

    x = dataidx.loc[(dataidx['month'] == i)].sum().Return
    q = dataidx.loc[(dataidx['month'] == i)].sum().month / float(i)
    returnpermonth = x / q * 100.0
    print(f" Month: {i} Summe Month: {q}  Summe cummuliert: {x}   Summe Return per month: {returnpermonth}  ")

print("***************")

for i in range(1, 52):

    x = dataidx.loc[(dataidx['week'] == i)].sum().Return
    q = dataidx.loc[(dataidx['week'] == i)].sum().week / float(i)
    returnperweek = x / q * 100.0

    print(f" Week: {i} Summe Month: {q}  Summe cummuliert: {x}   Summe Return per week: {returnperweek}  ")

# absolute Values

for i in range(1, 13):

    mean = dataidx.loc[(dataidx['month'] == i)].mean(numeric_only=False).Close
    x = dataidx.loc[(dataidx['month'] == i)].mean(numeric_only=False).absreturn / mean *100.0
    q = dataidx.loc[(dataidx['month'] == i)].sum().month / float(i)

    print(f"Month: {i} Summe Month: {q}    Summe Return per month:  {x}   ")

print("***************")

sq = 0
xs = 0

for i in range(1, 54):  # TODO: Hier ist noch ein Fehler im Vergleich zum Excel.
    mean = dataidx.loc[(dataidx['week'] == i)].mean(numeric_only=False).Close
    x = dataidx.loc[(dataidx['week'] == i)].mean(numeric_only=False).absreturn / mean * 100.0
    q = dataidx.loc[(dataidx['week'] == i)].sum().week / float(i)
    # returnperweek = x / q * 100.0
    sq += q
    xs += dataidx.loc[(dataidx['week'] == i)].mean(numeric_only=False).absreturn
    print(f" Week: {i}  Summe Week: {q} Summe Return per week: {x}   Mean = {mean} ")

print(xs, sq)



