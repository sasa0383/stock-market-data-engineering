"""
Configuration file for Dashboard App
Contains server settings and database connection details
"""

# Server Configuration
HOST = "0.0.0.0"
PORT = 8000

# PostgreSQL Configuration
POSTGRES_HOST = "postgres_db"
POSTGRES_DB = "stock_data"
POSTGRES_USER = "postgres"
POSTGRES_PASSWORD = "postgres"

# API Configuration
API_VERSION = "v1"
API_PREFIX = f"/api/{API_VERSION}"

# Dashboard Configuration
DEFAULT_SYMBOLS = ["AAPL", "MSFT", "GOOGL", "AMZN", "TSLA"]
DEFAULT_TIMEFRAME = "1d"
REFRESH_INTERVAL = 60  # seconds
