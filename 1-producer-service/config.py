"""
Configuration for Producer Service
Includes Yahoo Finance settings, Kafka setup, and indicator config
"""

import os

# Yahoo Finance Intervals & Periods
# Format: { label: (yfinance_interval, yfinance_period) }
YAHOO_INTERVALS = {
    "1m":  ("1m", "7d"),
    "5m":  ("5m", "7d"),
    "10m": ("10m", "7d"),
    "30m": ("30m", "30d"),
    "60m": ("60m", "60d"),
    "1d":  ("1d", "6mo"),
}

# Price filter for symbol selection
PRICE_LIMIT = 20.0  # USD

# File paths
SYMBOL_CSV_PATH = "/app/data/symbols.csv"              # CSV with stock symbols
KAGGLE_CSV_PATH = "/app/data/kaggle_stock_data.csv"    # Historical data

# Kafka Configuration
KAFKA_BROKER = "kafka:9092"  # Match internal Docker hostname
TOPIC_TEMPLATE = "{symbol_lower}_{interval}_data"  # e.g., aapl_5m_data

# Scalping Indicator Settings (to be used in consumer stage)
SCALPING_INDICATORS = {
    "RSI": {"enabled": True, "params": {"window": 14}},
    "Stochastic": {"enabled": True, "params": {"k_window": 14, "d_window": 3}},
    "EMA": {"enabled": True, "windows": [5, 9, 13, 21]},
    "MACD": {"enabled": True, "params": {"fast": 12, "slow": 26, "signal": 9}},
    "BollingerBands": {"enabled": True, "params": {"window": 20, "std": 2}},
    "ATR": {"enabled": True, "params": {"window": 14}},
    "OBV": {"enabled": True},
    "VWAP": {"enabled": False}
}
