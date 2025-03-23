# Consumer Batch Processing

This service processes stock market data in scheduled batches using Apache Spark for data transformation and aggregation.

## Features

- Batch processing of stock market data
- Daily, weekly, and monthly aggregations
- Moving average calculations
- Data cleaning and preprocessing
- Advanced analytics including volatility and trend indicators

## Configuration

Edit `config.py` to modify:
- PostgreSQL connection details
- Batch processing frequency
- Lookback period for historical data
- Moving average periods

## Components

- **batch_processor.py**: Main batch processing logic
- **data_cleaner.py**: Data cleaning and preprocessing
- **aggregation.py**: Advanced aggregation and analytics

## Requirements

- Python 3.8+
- Apache Spark 3.3.0+
- PostgreSQL database for data storage
- PySpark and related dependencies

## Running Locally

1. Install dependencies:
```
pip install -r requirements.txt
```

2. Run the batch processor:
```
python batch_processor.py
```

## Docker

Build the Docker image:
```
docker build -t stock-batch-processor .
```

Run the container:
```
docker run --network=stock-market-data-engineering_default stock-batch-processor
```

## Data Processing

The service performs the following processing on the stock data:
- Data cleaning and validation
- Daily, weekly, and monthly aggregations
- Calculation of moving averages (7-day, 30-day, 90-day)
- Volatility metrics
- Trend indicators
- Volume profile analysis

## Output Tables

The processed data is stored in the following PostgreSQL tables:
- `stock_daily_aggregates`
- `stock_weekly_aggregates`
- `stock_monthly_aggregates`
- `stock_moving_averages`
