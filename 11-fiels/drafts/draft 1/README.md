# Stock Market Data Engineering Project

This project implements a comprehensive batch-processing data architecture for a data-intensive machine learning application focused on stock market data.

## Architecture Overview

The system follows a microservices architecture with the following components:

- **Producer Service**: Fetches real-time stock data from external APIs and publishes to Kafka
- **Kafka Broker**: Manages message queues for data processing
- **Consumer Services**:
  - **Stream Storage**: Processes real-time data using Spark Streaming
  - **Batch Processing**: Performs scheduled batch transformations using Apache Spark
  - **Dashboard**: Serves real-time stock analysis via FastAPI and interactive UI
  - **Trading Bot**: Implements automated trading strategies
  - **Data Storage**: Writes Kafka streams to PostgreSQL/MongoDB
- **Database**: PostgreSQL for relational data and Elasticsearch for search/analytics

## Project Structure

```
📂 stock-market-data-engineering/
│
├── 📂 producer-service/         # Fetches stock data & pushes to Kafka
├── 📂 kafka-broker/             # Kafka & Zookeeper setup
├── 📂 consumer-stream-storage/  # Real-time Kafka consumer
├── 📂 consumer-batch-processing/ # Batch processing with Apache Spark
├── 📂 consumer-dashboard/       # Web dashboard with FastAPI
├── 📂 consumer-trading-bot/     # Trading logic & real-time analysis
├── 📂 consumer-data-storage/    # Writes Kafka stream to databases
├── 📂 database/                 # PostgreSQL & Elasticsearch setup
├── 📂 config/                   # Global configuration files
├── 📂 data/                     # Sample datasets
│
├── docker-compose.yml           # Orchestrates the entire system
├── start.sh                     # Setup & initialization script
└── README.md                    # This file
```

## Key Features

- **Reliability**: Fault tolerance, data persistence, and error handling
- **Scalability**: Horizontal scaling through containerization and microservices
- **Maintainability**: Modular design, documentation, and monitoring
- **Security**: Data encryption, access control, and secure configurations
- **Governance**: Data lineage, quality checks, and compliance measures

## Getting Started

### Prerequisites

- Docker and Docker Compose
- Git
- Internet connection for downloading Docker images

### Installation

1. Clone the repository:
```
git clone https://github.com/yourusername/stock-market-data-engineering.git
cd stock-market-data-engineering
```

2. Run the start script:
```
chmod +x start.sh
./start.sh
```

This will:
- Start all services using Docker Compose
- Create necessary Kafka topics
- Initialize the database schema

### Accessing Services

- **Dashboard**: http://localhost:8000
- **Kafka**: localhost:29092
- **PostgreSQL**: localhost:5432
- **Elasticsearch**: http://localhost:9200

## Development

Each microservice can be developed and tested independently:

1. Navigate to the service directory:
```
cd producer-service
```

2. Install dependencies:
```
pip install -r requirements.txt
```

3. Run the service:
```
python main.py
```

## Docker Deployment

The entire system can be deployed using Docker Compose:

```
docker-compose up -d
```

To stop all services:
```
docker-compose down
```

## Data Flow

1. Producer Service fetches stock data from external APIs
2. Data is published to Kafka topics
3. Consumer services process the data in various ways:
   - Stream Storage processes real-time data
   - Batch Processing performs scheduled transformations
   - Trading Bot analyzes data for trading signals
   - Data Storage writes data to databases
4. Dashboard visualizes the processed data

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a new Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.
