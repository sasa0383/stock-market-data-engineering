"""
Configuration for Database Writer Service
Contains database connection details and Kafka settings
"""

# Kafka Configuration
KAFKA_BROKER = "kafka:9092"
STOCK_PRICES_TOPIC = "stock_prices"

# Database Configuration
DB_HOST = "postgres"
DB_PORT = 5432
DB_NAME = "stockdata"
DB_USER = "postgres"
DB_PASSWORD = "postgres"

# Batch Processing Configuration
BATCH_SIZE = 100  # Number of records to batch before committing
BATCH_TIMEOUT = 30  # Maximum seconds to wait before committing a batch

# Error Handling
MAX_RETRIES = 3  # Maximum number of retries for database operations
RETRY_DELAY = 5  # Seconds to wait between retries
