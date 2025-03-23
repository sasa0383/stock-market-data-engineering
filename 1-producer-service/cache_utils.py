import os
import json
from datetime import datetime, timedelta

# 🧩 Load cached symbol list from a local JSON file
def load_cached_symbols(cache_file="symbol_cache.json", max_age_minutes=60):
    if not os.path.exists(cache_file):
        return None

    with open(cache_file, "r") as f:
        data = json.load(f)

    try:
        cache_time = datetime.fromisoformat(data["timestamp"])
        if datetime.now() - cache_time < timedelta(minutes=max_age_minutes):
            return data["symbols"]
    except Exception:
        pass

    return None

# 💾 Save symbol list and timestamp to a local JSON file
def save_symbol_cache(symbols, cache_file="symbol_cache.json"):
    with open(cache_file, "w") as f:
        json.dump({
            "timestamp": datetime.now().isoformat(),
            "symbols": symbols
        }, f)
