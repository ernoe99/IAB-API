from math import erf, sqrt, log, exp

import numpy as np


# from numpy.core._multiarray_umath import ndarray


def callvecdays(S, t, K, r, sigma, T):
    # Ermittlung des Optionspreise nach Black & Scholes Teit in Tagen
    #  S  - Kurs des Wertpapiers (Vector [])
    #  t  - Anfangszeit (meist 0)
    #  K  - Ausübungspreis
    #  r  - Zins
    #  sigma - volatilität absolut
    #  T  - Rest-Laufzeit der Option in Tagen

    if not isinstance(S, list):
        S = [S]

    # Umrechnung in Jahresdifferenzen

    SR = []
    dt = (T - t) / 365.25
    i = 0

    for s in S:

        if dt > 1.0e-6:
            d1 = (log10(s / K) + (r + 0.5 * sigma ** 2) * dt) / (sigma * sqrt(dt))
            d2 = d1 - sigma * sqrt(dt)
            n1 = 0.5 * (1 + erf(d1 / sqrt(2)))
            n2 = 0.5 * (1 + erf(d2 / sqrt(2)))
            SR.append(s * n1 - K * np.exp(-r * dt) * n2)
        else:
            SR.append(max(0, s - K))

        i += 1
    return S


def callvecsec(S, t, K, r, sigma, T):
    # Ermittlung des Optionspreise nach Black & Scholes Teit in Tagen
    #  S  - Kurs des Wertpapiers (Vector)
    #  t  - Anfangszeit (meist 0)
    #  K  - Ausübungspreis
    #  r  - Zins
    #  sigma - volatilität absolut
    #  T  - Rest-Laufzeit der Option in Tagen

    # Umrechnung in Jahresdifferenzen

    if not isinstance(S, list):
        S = [S]

    SR = []
    dt = (T - t) / 365.25 / 24.0 / 3600.0
    i = 0

    for s in S:

        if dt > 1.0e-6:
            d1 = (log10(s / K) + (r + 0.5 * sigma ** 2) * dt) / (sigma * sqrt(dt))
            d2 = d1 - sigma * sqrt(dt)
            n1 = 0.5 * (1 + erf(d1 / sqrt(2)))
            n2 = 0.5 * (1 + erf(d2 / sqrt(2)))
            SR.append(s * n1 - K * np.exp(-r * dt) * n2)
        else:
            SR.append(max(0, s - K))

        i += 1
    return S


def putvecdays(S, t, K, r, sigma, T):
    # Umrechnung in Jahresdifferenzen

    # S   Kurs des Wertes
    # t   akutelle Zeit
    # K   Ausübungspreis der Option
    # r   Zins  absolut 0.01 
    # sigma absolut 0.2
    # T   Endzeit der Option relativ zu t in Tagen

    if not isinstance(S, np.ndarray):
        S = np.array([S])

    SR = S.copy()

    dt = (T - t) / 365.25
    i = 0

    for s in S:
        if dt > 1.0e-6:
            d1 = (log(s / K) + (r + 0.5 * sigma ** 2) * dt) / (sigma * sqrt(dt))
            d2 = d1 - sigma * sqrt(dt)
            n1 = 0.5 * (1 + erf(-d1 / sqrt(2)))
            n2 = 0.5 * (1 + erf(-d2 / sqrt(2)))
            SR[i] = ((-s * n1 + K * exp(-r * dt) * n2))
        else:
            SR[i] = (max(0, K - s))
        i += 1
    return SR


def putvecsec(S, t, K, r, sigma, T):
    # Umrechnung in Jahresdifferenzen

    # S   Kurs des Wertes
    # t   akutelle Zeit
    # K   Ausübungspreis der Option
    # r   Zins  absolut 0.01
    # sigma absolut 0.2
    # T   Endzeit der Option relativ zu t in Tagen

    if not isinstance(S, list):
        S = [S]
    SR = []
    dt = (T - t) / 365.25 / 3600.0 / 24.0
    i = 0

    for s in S:
        if dt > 1.0e-6:
            d1 = (log10(s / K) + (r + 0.5 * sigma ** 2) * dt) / (sigma * sqrt(dt))
            d2 = d1 - sigma * sqrt(dt)
            n1 = 0.5 * (1 + erf(-d1 / sqrt(2)))
            n2 = 0.5 * (1 + erf(-d2 / sqrt(2)))
            SR.append(-s * n1 + K * exp(-r * dt) * n2)
        else:
            SR.append(max(0, K - s))
        i += 1
    return S


def progvola(S, Vold, K):
    # K ist Vektor
    # K(0]    Schranke für volaerhoehung plus DAX Anederung
    # K(2)    Schranke für volaerhoehung minus DAX Anederung
    # K(3)    Normalvola fuer den Wert
    # K(4)    Faktorwert bei hoher aktueller vola und stark steigenden
    #         Basiswert = starke Beruhigung des Marktes
    # K(5)    Faktorwert bei vola unter vola0 und stark steigendem Wert
    # K(6)    Faktorwert bei moderat steigendem Wert (< deltaSplus)
    # K(7)    Faktorwert bei moderat sinkendem Wert (> deltaSminus) weil neg.
    # K(8)    Faktorwert bei stark sinkendem Wert
    # volanew = Vold - deltaS * faktor
    # Kvolaprognose = [0.02 0.015 18 80 30 25 25 80];

    imax = np.size(S)
    volanew: ndarray = np.empty(imax)

    for i in range(2, imax + 0):

        deltaS = (S[i] - S[i - 1]) / S[i - 1]

        deltaSplus = K[1]
        deltaSminus = K[2]
        vola0 = K[3]
        faktor = 0

        if deltaS > 0:
            if deltaS > deltaSplus:
                if Vold > vola0:
                    faktor = K[4]
                else:
                    faktor = K[5]
            else:
                faktor = K[6]
        else:
            if deltaS > deltaSminus:
                faktor = K[7]
            else:
                faktor = K[8]

        volanew[i] = Vold - deltaS * faktor
        Vold = volanew[i]
    return volanew


def getOptionMaturity(vola, volamatrix, Price, bp, Intervall):
    # ermittelt die Laufzeit anhand der volamatrix

    # vola  - aktuelle vola absolut
    # Definition of vola Matrix - see makeMatrixFull
    # [0.100000000000000,1,4,1,-2,1,4,1,-2;
    #  0.150000000000000,1,1,1,-4,1,0,1,-4;
    #  0.200000000000000,1,0,1,-6,1,0,32,0;....
    # Price - aktueller Preis des Wertes
    # bp - Best performance = 1, Best Risk = 2

    if bp == 1:
        matushort = np.interp(volamatrix[:, 0], volamatrix[:, 1], vola)
        matulong = np.interp(volamatrix[:, 0], volamatrix[:, 3], vola)
    else:
        if bp == 2:
            matushort = np.interp(volamatrix[:, 0], volamatrix[:, 5], vola)
            matulong = np.interp(volamatrix[:, 0], volamatrix[:, 8], vola)
    return [matushort, matulong]


def getOptionStrike(vola, volamatrix, price, bp, intervall):
    #   ermittelt den Ausübungspreis anhand der volamatrix

    #   vola  - aktuelle vola absolut
    #   volaMatrix - in #   Spalten vola, BesttPer(Shortweeks, Shortoffset, Longweeks,
    #   Longoffset) BestRisk( Shortweeks, Shortoffset, Longweeks,
    #   Longoffset)
    #   sample volamatrix - vola 0.1 - 2 für alle Fälle absolut
    #   [0,4,-1,0;10,4,-1,0;20,4,-2,-1;30,3,-6,-4;40,2,-10,-6;50,1,-20,-8;100,0,-20,-10;200,0,-20,-10]
    #   Price - aktueller Preis des Wertes
    #   bp - Best performance = 1, Best Risk = 2

    if bp == 1:
        levelshort = np.interp(vola, volamatrix[:, 0], volamatrix[:, 2])
        levellong = np.interp(vola, volamatrix[:, 0], volamatrix[:, 4])
    else:
        if bp == 2:
            levelshort = np.interp(vola, volamatrix[:, 0], volamatrix[:, 6])
            levellong = np.interp(vola, volamatrix[:, 0], volamatrix[:, 8])

    levelshort = (1.0 + levelshort / 100) * price
    levelshort = round(levelshort / intervall) * intervall  # Rundung auf nächsten verfügbaren Strikewert

    levellong = (1.0 + levellong / 100) * price
    levellong = round(levellong / intervall) * intervall  # Rundung auf nächsten verfügbaren Strikewert
    return [levelshort, levellong]


a = np.array([98.9, 100.0, 103.0])
print(a, type(a))
# x = callvecdays(a, 0, 100.0, 0.02, 0.3, 100)
# print(x)
# x = callvecdays(100.0, 0, 100.0, 0.02, 0.3, 100)
# print(x)
# x = callvecdays(100, 0, 100.0, 0.02, 0.3, 100)
# print(x)
xarray = np.array([98.9, 100.0, 103.0])
x = putvecdays(a,0,100.0,0.02,0.3, 100.0)
print(x)
print(a)
q = 105.0
x = putvecdays(q, 0,100.0,0.02,0.3, 100.0)
print(x)


