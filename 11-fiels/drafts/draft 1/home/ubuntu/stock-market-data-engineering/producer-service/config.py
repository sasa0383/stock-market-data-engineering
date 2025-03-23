"""
Configuration file for Producer Service
Contains API keys, Kafka settings, and other configuration parameters
"""

# Kafka Configuration
KAFKA_BROKER = "kafka:9092"
KAFKA_TOPIC_STOCK_PRICES = "stock_prices"
KAFKA_TOPIC_MARKET_TRENDS = "market_trends"

# Stock Symbols to track
STOCK_SYMBOLS = ["AAPL", "MSFT", "GOOGL", "AMZN", "META", "TSLA", "NVDA", "JPM", "V", "WMT"]

# API Configuration
API_KEY = "YOUR_API_KEY"  # Replace with actual API key in production
API_BASE_URL = "https://query1.finance.yahoo.com/v8/finance/chart"

# Fetch interval in seconds
FETCH_INTERVAL = 60  # Fetch data every minute

# Retry Configuration
MAX_RETRIES = 3
RETRY_DELAY = 5  # seconds
