import pandas as pd
import ta
from config import SCALPING_INDICATORS

def add_scalping_indicators(df):
    df = df.copy()

    # RSI
    if SCALPING_INDICATORS.get("RSI", {}).get("enabled"):
        window = SCALPING_INDICATORS["RSI"]["params"]["window"]
        df["RSI"] = ta.momentum.RSIIndicator(df["close"], window=window).rsi()

    # Stochastic
    if SCALPING_INDICATORS.get("Stochastic", {}).get("enabled"):
        df["Stoch_K"] = ta.momentum.StochasticOscillator(
            high=df["high"], low=df["low"], close=df["close"]
        ).stoch()

    # EMA
    if SCALPING_INDICATORS.get("EMA", {}).get("enabled"):
        for w in SCALPING_INDICATORS["EMA"]["windows"]:
            df[f"EMA_{w}"] = ta.trend.EMAIndicator(df["close"], window=w).ema_indicator()

    # MACD
    if SCALPING_INDICATORS.get("MACD", {}).get("enabled"):
        macd = ta.trend.MACD(df["close"])
        df["MACD"] = macd.macd()
        df["MACD_signal"] = macd.macd_signal()

    # Bollinger Bands
    if SCALPING_INDICATORS.get("BollingerBands", {}).get("enabled"):
        bb = ta.volatility.BollingerBands(df["close"])
        df["BB_upper"] = bb.bollinger_hband()
        df["BB_lower"] = bb.bollinger_lband()

    # ATR
    if SCALPING_INDICATORS.get("ATR", {}).get("enabled"):
        atr = ta.volatility.AverageTrueRange(df["high"], df["low"], df["close"])
        df["ATR"] = atr.average_true_range()

    # OBV
    if SCALPING_INDICATORS.get("OBV", {}).get("enabled"):
        df["OBV"] = ta.volume.OnBalanceVolumeIndicator(df["close"], df["volume"]).on_balance_volume()

    return df
