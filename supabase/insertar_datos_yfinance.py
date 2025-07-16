import requests
import yfinance as yf
from datetime import datetime

# Supabase config
SUPABASE_URL = "https://hgsutzzwbssbqfibrnyw.supabase.co/rest/v1/apple_stock_data"
API_KEY = "sb_publishable_EUe5TZWME9W4V_gLcmhubA_yqxEnOpp"

headers = {
    "apikey": API_KEY,
    "Authorization": f"Bearer {API_KEY}",
    "Content-Type": "application/json"
}

# Descargar datos en tiempo real de AAPL (último minuto)
data = yf.download(tickers='AAPL', period='1d', interval='1m')

# Tomar solo el último registro
ultimo_dato = data.tail(1)

# Convertir a JSON y enviar a Supabase
for index, row in ultimo_dato.iterrows():
    data_row = {
        "ticker": "AAPL",
        "timestamp": index.isoformat(),
        "open": float(row["Open"]),
        "high": float(row["High"]),
        "low": float(row["Low"]),
        "close": float(row["Close"]),
        "volume": int(row["Volume"])
    }

    response = requests.post(SUPABASE_URL, json=data_row, headers=headers)
    print(f"Status: {response.status_code}")
    print(response.text)
