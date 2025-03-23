"""
Configuration file for Trading Bot
Contains trading strategies, risk parameters, and database connection details
"""

# Kafka Configuration
KAFKA_BROKER = "kafka:9092"
KAFKA_TOPIC_STOCK_PRICES = "stock_prices"
KAFKA_TOPIC_TRADING_SIGNALS = "trading_signals"

# PostgreSQL Configuration
POSTGRES_HOST = "postgres_db"
POSTGRES_DB = "stock_data"
POSTGRES_USER = "postgres"
POSTGRES_PASSWORD = "postgres"

# Trading Configuration
WATCHLIST = ["AAPL", "MSFT", "GOOGL", "AMZN", "META", "TSLA", "NVDA", "JPM", "V", "WMT"]
DEFAULT_QUANTITY = 10  # Default number of shares to trade

# Strategy Configuration
ACTIVE_STRATEGIES = [
    "moving_average_crossover",
    "rsi_strategy",
    "bollinger_bands"
]

STRATEGY_WEIGHTS = {
    "moving_average_crossover": 2,
    "rsi_strategy": 1,
    "bollinger_bands": 1
}

# Trading Thresholds
BUY_THRESHOLD = 2   # Minimum score to trigger a buy
SELL_THRESHOLD = 2  # Minimum score to trigger a sell

# Risk Management
MAX_POSITION_SIZE = 100  # Maximum shares per position
MAX_POSITIONS = 5        # Maximum number of concurrent positions
STOP_LOSS_PERCENT = 5    # Stop loss percentage
TAKE_PROFIT_PERCENT = 10 # Take profit percentage
