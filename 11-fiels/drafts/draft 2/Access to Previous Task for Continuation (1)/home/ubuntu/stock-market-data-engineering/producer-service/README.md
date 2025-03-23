# Producer Service

## Overview
The Producer Service is responsible for fetching real-time stock market data from external APIs and publishing it to Kafka topics for downstream processing. This service acts as the data ingestion layer of our stock market data engineering pipeline.

## Features
- Fetches stock data for multiple symbols at configurable intervals
- Publishes data to Kafka topics with proper error handling and retries
- Configurable API endpoints and parameters
- Robust logging for monitoring and debugging

## Configuration
Edit the `config.py` file to customize:
- `API_KEY`: Your API key for the financial data provider
- `API_URL_TEMPLATE`: The URL template for the API endpoint
- `KAFKA_BROKER`: Kafka broker address (default: "kafka:9092")
- `TOPIC`: Kafka topic to publish data to (default: "stock_prices")
- `FETCH_INTERVAL`: Time between API calls in seconds (default: 60)
- `SYMBOLS`: List of stock symbols to track

## Requirements
- Python 3.9+
- requests
- kafka-python
- python-dotenv

## Usage
1. Install dependencies:
   ```
   pip install -r requirements.txt
   ```

2. Run the service:
   ```
   python main.py
   ```

## Docker Usage
Build the Docker image:
```
docker build -t stock-producer-service .
```

Run the container:
```
docker run --network=stock-market-data-engineering_default stock-producer-service
```

## Data Flow
1. Service fetches stock data from the financial API
2. Data is formatted and enriched with timestamps
3. Messages are published to the Kafka topic
4. Downstream consumers process the data for various purposes

## Error Handling
- Connection issues with the API are logged and retried
- Kafka connection failures are handled with retries
- Invalid data responses are logged and skipped
