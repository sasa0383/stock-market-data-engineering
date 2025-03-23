"""
Configuration file for DB Writer
Contains database connection details and batch processing parameters
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

# MongoDB Configuration (for future use)
MONGODB_HOST = "mongo_db"
MONGODB_PORT = 27017
MONGODB_DB = "stock_data"
MONGODB_USER = "mongodb"
MONGODB_PASSWORD = "mongodb"

# Batch Processing Configuration
BATCH_SIZE = 100  # Number of records to batch before writing
BATCH_TIMEOUT = 30  # Maximum seconds to wait before writing a batch
