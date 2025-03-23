import pandas as pd
import yfinance as yf
from config import PRICE_LIMIT, SYMBOL_CSV_PATH
from tqdm import tqdm
from cache_utils import load_cached_symbols, save_symbol_cache

def get_symbols_below_price():
    # 🧠 Try loading from cache first
    cached = load_cached_symbols()
    if cached:
        print(f"🟢 Using cached symbol list ({len(cached)} symbols)")
        return cached

    # 🔁 Else fetch and filter manually
    df = pd.read_csv(SYMBOL_CSV_PATH)
    filtered = []

    for symbol in tqdm(df["symbol"].dropna().unique(), desc="Filtering Symbols"):
        try:
            ticker = yf.Ticker(symbol)
            price = ticker.info.get("regularMarketPrice")
            if price and price <= PRICE_LIMIT:
                filtered.append(symbol)
        except Exception:
            continue

    # 💾 Save filtered list to cache
    save_symbol_cache(filtered)
    return filtered
