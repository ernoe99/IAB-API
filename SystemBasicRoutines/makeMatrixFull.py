import numpy as np
import pandas as pd

from blackscholes import callvecdays, putvecdays


def genericStock(matk, volak, oomk, matl, volal, ooml, putcall, dKurse):
    price = 100.0
    zins = 0.01

    x = price * (1 + dKurse)

    strikeK = price * (1 + oomk / 100.0)
    strikeL = price * (1 + ooml / 100.0)

    if putcall == 1:
        valk = putvecdays(price, 0, strikeK, zins, volak, matk * 7)
        vall = putvecdays(price, 0, strikeL, zins, volal, matl * 7)
        valkend = putvecdays(x, 0, strikeK, zins, volak, (matk - 1) * 7)
        vallend = putvecdays(x, 0, strikeL, zins, volal, (matl - 1) * 7)
    else:
        valk = callvecdays(price, 0, strikeK, zins, volak, matk * 7)
        vall = callvecdays(price, 0, strikeL, zins, volal, matl * 7)
        valkend = callvecdays(x, 0, strikeK, zins, volak, (matk - 1) * 7)
        vallend = callvecdays(x, 0, strikeL, zins, volal, (matl - 1) * 7)

    return (valk - valkend) + (vallend - vall)


def makeMatrixFull(Kurse, putcall, ticker,
                   volas=None, shmat=[1, 2, 4], shoff=[-2, -1, 0, 1, 2, 4],
                   lomat=[1, 2, 4, 8, 16, 32, 52], looff = [-50, -8, -6, -4, -2, -1, 0]):  # 1 ist putsystem 0 = callsystem

    if volas is None:
        volas = [5, 10, 12.5, 15, 17.5, 20, 25, 30, 35, 40, 50, 60, 70, 80, 90, 100, 120, 150,
                 200]  # for low volas like GLD]

    dKurse = np.arange(Kurse.size - 1) * 1.0

    for item in np.arange(Kurse.size - 1):
        # print(item, Kurse[item], Kurse[item + 1])
        # print((Kurse[item + 1] - Kurse[item]) / Kurse[item])
        dKurse[item] = (Kurse[item + 1] - Kurse[item]) / Kurse[item]

    vola_matrix = []

    with pd.ExcelWriter("..\\output\\" + ticker + "\\VolaDetails.xlsx") as writer:

        for vola in volas:
            shvol = vola / 100.0

            lovol = shvol


            index = 0

            erg = []

            for i in shmat:
                for j in shoff:
                    for ii in lomat:
                        for jj in looff:
                            pl = genericStock(i, shvol, j, ii, lovol, jj, putcall, dKurse)
                            risk = abs(jj - j)
                            erg.append(
                                [i, shvol, j, ii, lovol, jj, pl.sum(), pl.max(), pl.min(), risk + 5.0,
                                 pl.sum() / (risk + 5.0)])

            df = pd.DataFrame(erg,
                              columns=["Maturity Short", "Vola Short", "Offset Short", "Maturity Long", "Vola Long",
                                       "Offset Long",
                                       "Sum PL", "Max PL", "Min PL", " Risk +5%", "Summe PL / Risk"])
            df = df.sort_values(by='Sum PL', ascending=False, ignore_index=True)  # Index beginnt wieder mit 0
            # print(df.head(10))
            sheet = "Perf" + str(vola)
            df.to_excel(writer, sheet_name=sheet)

            dfrisk = df.sort_values(by='Summe PL / Risk', ascending=False, ignore_index=True)
            # print(dfrisk.head(10))
            sheet = "Risk" + str(vola)
            dfrisk.to_excel(writer, sheet_name=sheet)

            vola_matrix.append([df.loc[0, "Vola Short"] * 100.0,
                                df.loc[0, "Maturity Short"], df.loc[0, "Offset Short"],
                                df.loc[0, "Maturity Long"], df.loc[0, "Offset Long"],
                                dfrisk.loc[0, "Maturity Short"], dfrisk.loc[0, "Offset Short"],
                                dfrisk.loc[0, "Maturity Long"], dfrisk.loc[0, "Offset Long"]])

    vm = pd.DataFrame(vola_matrix, columns=[" Volatility", "Maturity Short", "Offset Short", "Maturity Long",
                                            "Offset Long", "Maturity Short", "Offset Short", "Maturity Long",
                                            "Offset Long"])
    print(vm)
    vm.to_excel("..\\output\\" + ticker + "\\Vola_Matrix.xlsx")

    return vm.to_numpy()

# df_kurse = pd.read_excel('Kurse.xlsx')
# kurse = np.array(df_kurse['Close'])
#
# putcall = 1
#
# x = putvecdays(100,0,98,0.01,0.05,1.0)
#
# import time
# start_time = time.time()
# makeMatrixFull(kurse, putcall)
# print("--- %s seconds ---" % (time.time() - start_time))
