import requests
import pandas as pd
import io

API_KEY = 'tuQt2ur25Y7hTdGYdqI2VrE4dueVA8Xk'
POLYGON_API = f"https://api.polygon.io/"

def get_symbols():
    url="https://pkgstore.datahub.io/core/nasdaq-listings/nasdaq-listed_csv/data/7665719fb51081ba0bd834fde71ce822/nasdaq-listed_csv.csv"
    s = requests.get(url).content
    companies = pd.read_csv(io.StringIO(s.decode('utf-8')))
    symbols = companies['Symbol'].tolist()
    return symbols


# SYMBOLS = get_symbols()

SYMBOLS = [
    # "AAPL",
    "TSLA"
]