import yfinance as yf

def obtener_datos_aapl():
    data = yf.download(tickers='AAPL', period='1d', interval='1m')
    data.reset_index(inplace=True)
    return data