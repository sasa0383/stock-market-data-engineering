"""
Configuration for Trading Bot Service
Contains API keys, trading strategies, and Kafka settings
"""

# Kafka Configuration
KAFKA_BROKER = "kafka:9092"
STOCK_PRICES_TOPIC = "stock_prices"
TRADING_ALERTS_TOPIC = "trading_alerts"

# API Configuration
API_KEY = "YOUR_API_KEY"  # Replace with your actual API key
API_BASE_URL = "https://api.iextrading.com/1.0"

# Symbols to Track
SYMBOLS_TO_TRACK = ["AAPL", "MSFT", "GOOGL", "AMZN", "META", "TSLA", "NVDA", "JPM", "V", "WMT"]

# Trading Strategies Configuration
TRADING_STRATEGIES = {
    "moving_average_crossover": {
        "short_window": 5,   # 5-period moving average
        "long_window": 20    # 20-period moving average
    },
    "rsi": {
        "window": 14,        # 14-period RSI
        "overbought": 70,    # Overbought threshold
        "oversold": 30       # Oversold threshold
    },
    "bollinger_bands": {
        "window": 20,        # 20-period moving average
        "num_std": 2         # 2 standard deviations
    }
}

# Risk Management Settings
RISK_MANAGEMENT = {
    "max_position_size": 0.05,  # Maximum 5% of portfolio per position
    "stop_loss_pct": 0.02,      # 2% stop loss
    "take_profit_pct": 0.05     # 5% take profit
}

# Backtesting Settings
BACKTEST_SETTINGS = {
    "start_date": "2023-01-01",
    "end_date": "2023-12-31",
    "initial_capital": 100000
}
