"""
Configuration file for Stream Consumer
Contains Kafka settings, database connection, and processing parameters
"""

# Kafka Configuration
KAFKA_BROKER = "kafka:9092"
KAFKA_TOPIC_STOCK_PRICES = "stock_prices"
KAFKA_TOPIC_MARKET_TRENDS = "market_trends"

# PostgreSQL Configuration
POSTGRES_URL = "jdbc:postgresql://postgres_db:5432/stock_data"
POSTGRES_USER = "postgres"
POSTGRES_PASSWORD = "postgres"

# Processing Configuration
WINDOW_DURATION = "5 minutes"
WATERMARK_DELAY = "10 minutes"

# Output Configuration
WRITE_TO_CONSOLE = True
WRITE_TO_POSTGRES = True
