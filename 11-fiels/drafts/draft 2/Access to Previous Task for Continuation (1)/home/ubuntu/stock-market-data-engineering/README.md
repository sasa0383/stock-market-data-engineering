# Stock Market Data Engineering Project

## Overview
This project implements a comprehensive data engineering pipeline for stock market data. It ingests, processes, stores, and analyzes stock market data using a microservices architecture with batch processing capabilities. The system is designed to be reliable, scalable, and maintainable, following best practices for data engineering.

## Architecture
The system follows a microservices architecture with the following components:

1. **Producer Service**: Fetches real-time stock data from financial APIs and publishes it to Kafka.
2. **Kafka Broker**: Serves as the central message queue for decoupling data producers from consumers.
3. **Consumer Services**:
   - **Stream Storage**: Processes real-time data using Spark Streaming.
   - **Batch Processing**: Performs scheduled batch transformations using Apache Spark.
   - **Dashboard**: Provides a web interface for data visualization.
   - **Trading Bot**: Implements trading strategies based on technical analysis.
   - **Data Storage**: Persists data to PostgreSQL database.
4. **Database**: PostgreSQL with TimescaleDB for time-series data and Elasticsearch for analytics.

![Architecture Diagram](https://mermaid.ink/img/pako:eNqNVE1v2zAM_SuETgOKJE7SdLcBw7ChwIAd1h12UGzG1mKLhiQnTYP89yHZnNcPbD3YEsnn9x5FUjdKOYNqpFrXDXpLb8Ys0Gg0Ey-Wd-gJDPqZsxXMHXpbw8JhA1PtLCzRLWFuDVZgHFoHM-0aWDhQBmEKM7SGlQMNM9SWZtqBnVuDDdg5OAcGDFrCWDhYkqKFJVhHn1NwDjNL3-ZgLZgJzLVboLPwqI1bwNQ4B9aCdWjgQZsGZtquyMpjDVZbA1PtLf2vgTttHLgJPGhXo4MHbT3M0FHwE3jQlYUFGrLy6GCBzk_gXlcGlto1E_isnYOVNjCnDCZwr2sDK-3JwwQetDGw1JWjKCZwr6sl-Qk8aPJDOQqYwJ02K1hpT5lM4LMxDm1NwU_gQZsVLHVFBU3gXlcrWOmKvE7gQVcGlroif8QHbSqYaUNRTeBOVxaWuqLiJ_CgTQ0zbSqKZgKftakpF_JKMUzgTlcGVrqiWiZwr2tDXU9OJvCgjYGFrqjpCdxrU8NcV9T_BO60WcFSV9TQBO61qWCuK2qLCdxpY2GhK2qNCTxoU8FMV9QeE_isK0vtQe0xgQdtKpjriqKZwGdtLKx0RfFP4F4bA0tdUQdM4EEbA3e6ohYhPzXMtakoqgncaVPBUlfUJhO416aCma4o-gncaWNgqStqlQk8amNgpg21zQTudGVhqStqnQnca1PDXFNME7jTxsJSV9RCE3jQxsBMVxTXBD5rY2GlDcU2gXttDCx1RTE-0aFGQ3E-0aFGQ7E-0aFGQzE_0aFGQ3E_0aFGQ7E_0aFGQyt4okONhtbwRIcaDa3iiQ41GlrHEx1qNLSSJzrUaGgtT3So0dBqnuhQo6H1PNGhRkMreqJDjYbW9ESHGg2t6okONRpa1xMdajS0sic61GhobbsdajS0utuhRkPru-1Qo6EV3naocW_9H9Z5Uis)

## Features
- **Real-time Data Ingestion**: Fetches stock market data from financial APIs.
- **Message Queuing**: Uses Kafka for reliable message delivery and decoupling.
- **Stream Processing**: Processes data in real-time using Spark Streaming.
- **Batch Processing**: Performs scheduled transformations and aggregations.
- **Data Storage**: Stores raw and processed data in PostgreSQL with TimescaleDB.
- **Search and Analytics**: Uses Elasticsearch for advanced search and analytics.
- **Visualization**: Provides a web dashboard for data visualization.
- **Trading Strategies**: Implements technical analysis strategies for trading signals.
- **Containerization**: Uses Docker for consistent deployment across environments.

## Prerequisites
- Docker and Docker Compose
- Financial API keys (e.g., Alpha Vantage, Financial Modeling Prep, IEX Cloud)
- At least 8GB of RAM for running all services

## Installation and Setup

### 1. Clone the Repository
```bash
git clone https://github.com/yourusername/stock-market-data-engineering.git
cd stock-market-data-engineering
```

### 2. Configure API Keys
Edit the `config/api_keys.json` file to add your financial API keys:
```json
{
  "financial_modeling_prep": "YOUR_API_KEY",
  "alpha_vantage": "YOUR_API_KEY",
  "iex_cloud": "YOUR_API_KEY"
}
```

### 3. Start the System
Run the startup script to initialize and start all services:
```bash
chmod +x start.sh
./start.sh
```

This script will:
- Create necessary configuration files if they don't exist
- Set up the required directory structure
- Start all services using Docker Compose
- Display access information for the various components

### 4. Access the Dashboard
Once all services are running, you can access the dashboard at:
```
http://localhost:8000
```

## Component Details

### Producer Service
The Producer Service fetches real-time stock data from financial APIs and publishes it to Kafka topics. It's configured to track multiple stock symbols and fetch data at regular intervals.

**Key Files:**
- `producer-service/main.py`: Main service logic
- `producer-service/config.py`: Configuration settings

### Kafka Broker
The Kafka Broker serves as the central message queue for the system, with Zookeeper for coordination. It includes a Kafka UI for monitoring and management.

**Key Files:**
- `kafka-broker/docker-compose.yml`: Kafka and Zookeeper setup
- `kafka-broker/kafka-config.sh`: Topic creation script

### Consumer Services

#### Stream Storage
Processes real-time stock data using Spark Streaming, calculating metrics with windowed aggregations.

**Key Files:**
- `consumer-stream-storage/stream_consumer.py`: Spark Streaming logic

#### Batch Processing
Performs scheduled batch processing of stock data, including cleaning, aggregation, and analysis.

**Key Files:**
- `consumer-batch-processing/batch_processor.py`: Main processing logic
- `consumer-batch-processing/data_cleaner.py`: Data cleaning functions
- `consumer-batch-processing/aggregation.py`: Aggregation functions

#### Dashboard
Provides a web interface for visualizing stock data and analytics.

**Key Files:**
- `consumer-dashboard/app.py`: FastAPI backend
- `consumer-dashboard/templates/index.html`: Main dashboard template
- `consumer-dashboard/static/js/dashboard.js`: Dashboard JavaScript

#### Trading Bot
Analyzes stock data and generates trading signals based on technical analysis strategies.

**Key Files:**
- `consumer-trading-bot/bot.py`: Trading logic
- `consumer-trading-bot/config.py`: Strategy configuration

#### Data Storage
Writes Kafka streams to PostgreSQL database with efficient batch processing.

**Key Files:**
- `consumer-data-storage/db_writer.py`: Database writer logic
- `consumer-data-storage/config.py`: Database configuration

### Database
The database component includes PostgreSQL with TimescaleDB for time-series data, Elasticsearch for search and analytics, and Kibana for visualization.

**Key Files:**
- `database/docker-compose.yml`: Database services setup
- `database/init.sql`: Schema initialization script

## Configuration
The system uses several configuration files:

- `config/kafka_settings.json`: Kafka broker and topic settings
- `config/db_settings.json`: Database connection details
- `config/api_keys.json`: API keys for financial data providers

## Deployment
The system is designed to be deployed using Docker Compose, which orchestrates all the services. The main `docker-compose.yml` file in the project root integrates all the individual components.

## Scaling
The system can be scaled in several ways:

- **Kafka**: Increase partitions for higher throughput
- **PostgreSQL**: Use TimescaleDB's hypertable partitioning for large datasets
- **Spark**: Adjust executor resources for better performance
- **Elasticsearch**: Add nodes to the cluster for higher capacity

## Monitoring
The system includes several monitoring points:

- **Kafka UI**: http://localhost:8080
- **Kibana**: http://localhost:5601
- **Docker Logs**: `docker-compose logs -f [service_name]`

## Troubleshooting

### Common Issues

1. **Services fail to start**
   - Check Docker logs: `docker-compose logs -f [service_name]`
   - Ensure you have enough system resources (RAM, CPU)

2. **No data in dashboard**
   - Verify the producer service is running: `docker-compose logs -f producer-service`
   - Check Kafka topics have messages: Use Kafka UI at http://localhost:8080

3. **Database connection issues**
   - Verify PostgreSQL is running: `docker-compose ps postgres`
   - Check database logs: `docker-compose logs -f postgres`

## Future Enhancements
- Add real-time streaming pipeline alongside batch processing
- Implement machine learning models for price prediction
- Add user authentication to the dashboard
- Integrate with trading platforms for automated trading
- Implement alerting system for price movements

## License
This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments
- Financial data provided by various financial APIs
- Built with open-source technologies: Apache Kafka, Apache Spark, PostgreSQL, Elasticsearch, and more
