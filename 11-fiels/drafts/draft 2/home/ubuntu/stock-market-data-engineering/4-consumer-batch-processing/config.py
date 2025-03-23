"""
Configuration for Batch Processing Service
Contains database connection details and table names
"""

# Database Configuration
DB_HOST = "postgres"
DB_PORT = 5432
DB_NAME = "stockdata"
DB_USER = "postgres"
DB_PASSWORD = "postgres"

# Table Names
SOURCE_TABLE = "stock_prices"
DAILY_AGG_TABLE = "stock_daily_aggregates"
WEEKLY_AGG_TABLE = "stock_weekly_aggregates"
MONTHLY_AGG_TABLE = "stock_monthly_aggregates"

# Batch Processing Configuration
BATCH_INTERVAL = "1d"  # Process data daily
LOOKBACK_PERIOD = "30d"  # Process last 30 days of data

# Spark Configuration
SPARK_EXECUTOR_MEMORY = "2g"
SPARK_EXECUTOR_CORES = 2
SPARK_DRIVER_MEMORY = "2g"
