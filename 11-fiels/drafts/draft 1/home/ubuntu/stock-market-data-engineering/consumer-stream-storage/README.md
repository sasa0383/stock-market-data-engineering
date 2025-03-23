# Consumer Stream Storage

This service consumes real-time stock data from Kafka topics and processes it using Apache Spark Streaming.

## Features

- Real-time consumption of stock price data from Kafka
- Stream processing with Apache Spark Streaming
- Calculation of moving averages and other aggregations
- Storage of processed data in PostgreSQL
- Configurable processing windows and parameters

## Configuration

Edit `config.py` to modify:
- Kafka broker address and topic names
- PostgreSQL connection details
- Processing parameters (window duration, watermark delay)
- Output options

## Requirements

- Python 3.8+
- Apache Spark 3.3.0+
- Kafka broker accessible at the configured address
- PostgreSQL database for storing processed data

## Running Locally

1. Install dependencies:
```
pip install -r requirements.txt
```

2. Run the service:
```
python stream_consumer.py
```

## Docker

Build the Docker image:
```
docker build -t stock-stream-consumer .
```

Run the container:
```
docker run --network=stock-market-data-engineering_default stock-stream-consumer
```

## Data Processing

The service performs the following processing on the incoming stock data:
- Parsing JSON messages from Kafka
- Converting timestamps to proper datetime format
- Calculating 5-minute moving averages for stock prices
- Computing max/min prices and average volume
- Storing aggregated results in PostgreSQL

## Output Schema

The processed data has the following schema:
```
symbol: STRING
window: {start: TIMESTAMP, end: TIMESTAMP}
avg_price: DOUBLE
max_price: DOUBLE
min_price: DOUBLE
avg_volume: DOUBLE
```
