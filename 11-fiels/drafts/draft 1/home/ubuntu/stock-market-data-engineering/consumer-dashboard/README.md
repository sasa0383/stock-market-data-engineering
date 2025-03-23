# Consumer Dashboard

This service provides a web-based dashboard for visualizing stock market data and analytics.

## Features

- Real-time stock price and volume charts
- Market summary with top gainers, losers, and most active stocks
- Stock metrics and moving averages
- Interactive UI with filtering by symbol and timeframe
- RESTful API for accessing stock data

## Configuration

Edit `config.py` to modify:
- Server host and port
- PostgreSQL connection details
- Default symbols and timeframes
- Refresh interval

## Components

- **app.py**: FastAPI application with API endpoints
- **templates/**: HTML templates for the dashboard
- **static/**: CSS, JavaScript, and other static assets

## Requirements

- Python 3.8+
- FastAPI and Uvicorn
- PostgreSQL database with stock data
- Web browser for accessing the dashboard

## Running Locally

1. Install dependencies:
```
pip install -r requirements.txt
```

2. Run the service:
```
uvicorn app:app --host 0.0.0.0 --port 8000
```

## Docker

Build the Docker image:
```
docker build -t stock-dashboard .
```

Run the container:
```
docker run -p 8000:8000 --network=stock-market-data-engineering_default stock-dashboard
```

## API Endpoints

- `GET /api/stocks`: List all available stock symbols
- `GET /api/stock/{symbol}`: Get stock data for a specific symbol
- `GET /api/aggregates/{symbol}`: Get aggregated data (daily, weekly, monthly)
- `GET /api/moving-averages/{symbol}`: Get moving averages
- `GET /api/market-summary`: Get market summary with top gainers, losers, and most active stocks

## Dashboard Access

Access the dashboard in your web browser at:
```
http://localhost:8000
```
