# Consumer Data Storage

This service consumes data from Kafka topics and writes it to PostgreSQL and MongoDB databases for persistent storage.

## Features

- Consumes real-time stock data from Kafka
- Batch processing for efficient database writes
- Support for both PostgreSQL and MongoDB
- Automatic table creation and index management
- Configurable batch sizes and timeouts

## Configuration

Edit `config.py` to modify:
- Kafka broker address and topic names
- PostgreSQL connection details
- MongoDB connection details (for future use)
- Batch processing parameters

## Components

- **db_writer.py**: Main database writer implementation
- **config.py**: Configuration parameters

## Requirements

- Python 3.8+
- Kafka broker accessible at the configured address
- PostgreSQL database for relational data storage
- MongoDB database for document storage (future use)
- Dependencies listed in requirements.txt

## Running Locally

1. Install dependencies:
```
pip install -r requirements.txt
```

2. Run the database writer:
```
python db_writer.py
```

## Docker

Build the Docker image:
```
docker build -t stock-db-writer .
```

Run the container:
```
docker run --network=stock-market-data-engineering_default stock-db-writer
```

## Database Schema

### PostgreSQL Tables

#### stock_prices
- id: SERIAL PRIMARY KEY
- symbol: VARCHAR(10) NOT NULL
- timestamp: BIGINT NOT NULL
- date: TIMESTAMP NOT NULL
- open: NUMERIC(10, 2) NOT NULL
- high: NUMERIC(10, 2) NOT NULL
- low: NUMERIC(10, 2) NOT NULL
- close: NUMERIC(10, 2) NOT NULL
- volume: BIGINT NOT NULL
- created_at: TIMESTAMP DEFAULT CURRENT_TIMESTAMP

#### trading_signals
- id: SERIAL PRIMARY KEY
- timestamp: TIMESTAMP NOT NULL
- symbol: VARCHAR(10) NOT NULL
- action: VARCHAR(10) NOT NULL
- price: NUMERIC(10, 2) NOT NULL
- quantity: INTEGER NOT NULL
- details: JSONB
- created_at: TIMESTAMP DEFAULT CURRENT_TIMESTAMP

## Batch Processing

The service implements batch processing to optimize database writes:
- Records are collected in memory until batch size is reached
- Batches are also committed based on a timeout to ensure timely processing
- Efficient bulk insert operations are used for better performance
