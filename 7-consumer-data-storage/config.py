import os

# Kafka Configuration
KAFKA_BROKER = os.getenv("KAFKA_BROKER", "kafka:9092")
KAFKA_TOPICS = [
    "kaggle_historical_data",
    "aapl_1m_data",
    "msft_1m_data",
    # Add more topics or load dynamically
]
KAFKA_GROUP_ID = "data_storage_group"

# PostgreSQL Configuration
DB_HOST = os.getenv("POSTGRES_HOST", "postgres")
DB_PORT = os.getenv("POSTGRES_PORT", "5432")
DB_NAME = os.getenv("POSTGRES_DB", "stock_data")
DB_USER = os.getenv("POSTGRES_USER", "postgres")
DB_PASSWORD = os.getenv("POSTGRES_PASSWORD", "postgres")
TARGET_TABLE = os.getenv("POSTGRES_TABLE", "raw_enriched_stock_data")
