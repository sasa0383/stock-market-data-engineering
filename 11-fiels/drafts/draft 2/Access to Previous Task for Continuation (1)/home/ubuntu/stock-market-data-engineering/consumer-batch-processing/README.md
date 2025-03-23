# Consumer Batch Processing

## Overview
The Consumer Batch Processing service processes stock market data in scheduled batches for analysis and aggregation. It performs data cleaning, transformation, and aggregation on historical stock data stored in PostgreSQL, and saves the results back to the database for reporting and visualization.

## Features
- Scheduled batch processing of stock data
- Data cleaning and outlier removal
- Multiple levels of aggregation (daily, weekly, monthly)
- Calculation of moving averages and trend detection
- Volatility and relative strength analysis
- Persistent storage of aggregated data

## Components
1. **Batch Processor**: Main processing logic for scheduled batch jobs
2. **Data Cleaner**: Functions for cleaning and preprocessing data
3. **Aggregation**: Functions for data aggregation and analysis

## Requirements
- Python 3.9+
- Apache Spark 3.3.0
- Pandas
- PostgreSQL connector

## Configuration
Edit the `config.py` file to customize:
- Database connection details (host, port, name, user, password)
- Table names for source and destination data
- Batch processing interval and lookback period
- Spark configuration parameters

## Usage
1. Install dependencies:
   ```
   pip install -r requirements.txt
   ```

2. Run the batch processor:
   ```
   python batch_processor.py
   ```

## Docker Usage
Build the Docker image:
```
docker build -t stock-batch-processor .
```

Run the container:
```
docker run --network=stock-market-data-engineering_default stock-batch-processor
```

## Data Flow
1. Service loads stock data from PostgreSQL
2. Data is cleaned and preprocessed
3. Multiple aggregations are performed (daily, weekly, monthly)
4. Advanced metrics are calculated (moving averages, trends, volatility)
5. Results are saved back to PostgreSQL for reporting

## Scheduling
This service is designed to be run on a schedule (e.g., daily) using a scheduler like Apache Airflow or cron. For example, to run daily at midnight:

```
0 0 * * * docker run --network=stock-market-data-engineering_default stock-batch-processor
```

## Output Tables
- `stock_daily_aggregates`: Daily price aggregations and metrics
- `stock_weekly_aggregates`: Weekly price aggregations
- `stock_monthly_aggregates`: Monthly price aggregations
