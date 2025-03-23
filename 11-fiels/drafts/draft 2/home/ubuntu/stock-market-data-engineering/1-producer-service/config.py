"""
Configuration for Producer Service
Contains API keys, Kafka topics, and update intervals
"""

# API Configuration
API_KEY = "YOUR_API_KEY"  # Replace with your actual API key
API_URL_TEMPLATE = "https://financialmodelingprep.com/api/v3/quote/{symbol}?apikey={api_key}"

# Kafka Configuration
KAFKA_BROKER = "kafka:9092"
TOPIC = "stock_prices"

# Fetch Configuration
FETCH_INTERVAL = 60  # Fetch data every 60 seconds
SYMBOLS = ["AAPL", "MSFT", "GOOGL", "AMZN", "META", "TSLA", "NVDA", "JPM", "V", "WMT"]  # Top 10 stocks to track
