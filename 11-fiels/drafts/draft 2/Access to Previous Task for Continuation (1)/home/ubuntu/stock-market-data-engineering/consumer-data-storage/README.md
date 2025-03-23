# Consumer Data Storage

## Overview
The Consumer Data Storage service is responsible for persisting stock market data from Kafka streams to a PostgreSQL database. It provides reliable, efficient storage of real-time and batch-processed data for later analysis and visualization.

## Features
- Consumes stock price data from Kafka topics
- Efficiently writes data to PostgreSQL with batch processing
- Creates and maintains database schema
- Handles data type conversions and timestamp formatting
- Implements error handling and retry logic
- Optimizes database performance with appropriate indexes

## Components
1. **Database Writer**: Main logic for consuming Kafka messages and writing to database
2. **Batch Processing**: Efficient batch inserts for better performance
3. **Schema Management**: Creates tables and indexes if they don't exist

## Requirements
- Python 3.9+
- Kafka Python client
- PostgreSQL connector (psycopg2)

## Configuration
Edit the `config.py` file to customize:
- Kafka broker address and topics
- Database connection details (host, port, name, user, password)
- Batch processing parameters (size, timeout)
- Error handling settings (retries, delay)

## Usage
1. Install dependencies:
   ```
   pip install -r requirements.txt
   ```

2. Run the database writer:
   ```
   python db_writer.py
   ```

## Docker Usage
Build the Docker image:
```
docker build -t stock-db-writer .
```

Run the container:
```
docker run --network=stock-market-data-engineering_default stock-db-writer
```

## Data Flow
1. Service consumes stock price data from Kafka topic
2. Data is batched for efficient database operations
3. Batches are committed to PostgreSQL based on size or timeout
4. Database tables and indexes are automatically created if needed

## Database Schema
### stock_prices
- `id`: Serial primary key
- `symbol`: Stock symbol (VARCHAR)
- `price`: Stock price (NUMERIC)
- `volume`: Trading volume (NUMERIC)
- `timestamp`: Data timestamp (TIMESTAMP)
- `fetch_timestamp`: Unix timestamp when data was fetched (BIGINT)

### stock_metrics
- `id`: Serial primary key
- `symbol`: Stock symbol (VARCHAR)
- `window_start`: Start of aggregation window (TIMESTAMP)
- `window_end`: End of aggregation window (TIMESTAMP)
- `avg_price`: Average price in window (NUMERIC)
- `max_price`: Maximum price in window (NUMERIC)
- `min_price`: Minimum price in window (NUMERIC)
- `avg_volume`: Average volume in window (NUMERIC)
- `created_at`: Record creation timestamp (TIMESTAMP)
