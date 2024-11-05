import streamlit as st
import numpy as np
from scipy.stats import norm


def black_scholes(S, K, T, r, sigma, option_type='call'):
    d1 = (np.log(S / K) + (r + 0.5 * sigma ** 2) * T) / (sigma * np.sqrt(T))
    d2 = d1 - sigma * np.sqrt(T)

    if option_type == 'call':
        option_price = S * norm.cdf(d1) - K * np.exp(-r * T) * norm.cdf(d2)
    else:  # Put option
        option_price = K * np.exp(-r * T) * norm.cdf(-d2) - S * norm.cdf(-d1)

    return option_price


st.title('Optionspreisrechner')

# Eingabefelder
S = st.number_input('Aktueller Aktienkurs', min_value=0.01, value=100.0)
K = st.number_input('Ausübungspreis', min_value=0.01, value=100.0)
T = st.number_input('Zeit bis zur Fälligkeit (in Jahren)', min_value=0.01, value=1.0)
r = st.number_input('Risikofreier Zinssatz (in Dezimalform)', min_value=0.0, value=0.05)
sigma = st.number_input('Volatilität (in Dezimalform)', min_value=0.01, value=0.2)
option_type = st.selectbox('Optionstyp', ['call', 'put'])

if st.button('Preis berechnen'):
    option_price = black_scholes(S, K, T, r, sigma, option_type)
    st.success(f'Der Preis der {option_type.capitalize()}-Option beträgt: {option_price:.2f}')

st.markdown('''
## Erläuterung der Parameter:
- **Aktueller Aktienkurs (S)**: Der aktuelle Marktpreis der zugrunde liegenden Aktie.
- **Ausübungspreis (K)**: Der Preis, zu dem die Option ausgeübt werden kann.
- **Zeit bis zur Fälligkeit (T)**: Die verbleibende Zeit bis zum Ablauf der Option in Jahren.
- **Risikofreier Zinssatz (r)**: Der angenommene risikofreie Zinssatz für die Laufzeit der Option.
- **Volatilität (sigma)**: Die erwartete Schwankungsbreite des Aktienkurses, ausgedrückt als Standardabweichung.
- **Optionstyp**: 'Call' für das Recht zu kaufen, 'Put' für das Recht zu verkaufen.
''')