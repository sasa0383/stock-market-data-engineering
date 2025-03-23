# Consumer Stream Storage

## Overview
The Consumer Stream Storage service processes real-time stock market data from Kafka using Apache Spark Streaming. It performs windowed aggregations on the streaming data and stores the results in PostgreSQL for further analysis and visualization.

## Features
- Real-time consumption of stock data from Kafka
- Windowed aggregations (5-minute windows) for calculating metrics
- Calculation of average, maximum, and minimum prices
- Storage of processed data in PostgreSQL
- Watermarking for handling late data

## Requirements
- Python 3.9+
- Apache Spark 3.3.0
- Kafka Python client
- PostgreSQL connector

## Configuration
The service is configured to:
- Connect to Kafka broker at `kafka:9092`
- Subscribe to the `stock_prices` topic
- Process data with 5-minute windows and 10-minute watermarks
- Write results to PostgreSQL database

## Usage
1. Install dependencies:
   ```
   pip install -r requirements.txt
   ```

2. Run the service:
   ```
   python stream_consumer.py
   ```

## Docker Usage
Build the Docker image:
```
docker build -t stock-stream-consumer .
```

Run the container:
```
docker run --network=stock-market-data-engineering_default stock-stream-consumer
```

## Data Flow
1. Service consumes messages from the Kafka `stock_prices` topic
2. JSON messages are parsed according to the defined schema
3. Timestamps are converted to appropriate format
4. Windowed aggregations are performed on the data
5. Results are written to both console (for debugging) and PostgreSQL

## Schema
The service expects messages with the following schema:
```
{
  "symbol": "AAPL",
  "price": 150.25,
  "volume": 1000000,
  "timestamp": "2023-01-01T12:00:00Z",
  "fetch_timestamp": 1672574400
}
```

## Output
The service produces aggregated metrics including:
- Average price per 5-minute window
- Maximum price per 5-minute window
- Minimum price per 5-minute window
- Average volume per 5-minute window
