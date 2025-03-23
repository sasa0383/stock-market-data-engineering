# Producer Service

This service fetches real-time stock data from Yahoo Finance API and publishes it to Kafka topics for downstream processing.

## Features

- Fetches stock price data for configurable list of symbols
- Publishes data to Kafka topics in a standardized format
- Implements error handling and retry logic
- Configurable fetch intervals

## Configuration

Edit `config.py` to modify:
- Stock symbols to track
- Kafka broker address and topic names
- API configuration
- Fetch interval

## Requirements

- Python 3.10+
- Kafka broker accessible at the configured address
- Internet access to fetch stock data from Yahoo Finance

## Running Locally

1. Install dependencies:
```
pip install -r requirements.txt
```

2. Run the service:
```
python main.py
```

## Docker

Build the Docker image:
```
docker build -t stock-producer-service .
```

Run the container:
```
docker run --network=stock-market-data-engineering_default stock-producer-service
```

## Data Format

The service publishes data in the following format:
```json
{
  "symbol": "AAPL",
  "timestamp": 1647360000,
  "datetime": "2022-03-15T16:00:00",
  "open": 155.23,
  "high": 157.82,
  "low": 154.46,
  "close": 157.12,
  "volume": 76532100
}
```
