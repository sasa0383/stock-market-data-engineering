"""
Configuration file for Batch Processor
Contains database connection details and processing parameters
"""

# PostgreSQL Configuration
POSTGRES_URL = "jdbc:postgresql://postgres_db:5432/stock_data"
POSTGRES_USER = "postgres"
POSTGRES_PASSWORD = "postgres"

# Processing Configuration
BATCH_FREQUENCY = "daily"  # Options: daily, weekly, monthly
LOOKBACK_PERIOD = 90  # Days of historical data to process

# Moving Average Periods
MA_PERIODS = [7, 30, 90]  # Days for moving average calculations

# Output Tables
TABLE_DAILY_AGGREGATES = "stock_daily_aggregates"
TABLE_WEEKLY_AGGREGATES = "stock_weekly_aggregates"
TABLE_MONTHLY_AGGREGATES = "stock_monthly_aggregates"
TABLE_MOVING_AVERAGES = "stock_moving_averages"
