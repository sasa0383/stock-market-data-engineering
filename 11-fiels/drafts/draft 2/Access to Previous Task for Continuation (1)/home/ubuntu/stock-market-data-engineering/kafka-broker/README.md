# Kafka Broker

## Overview
The Kafka Broker component serves as the central message queue for our stock market data engineering pipeline. It provides a reliable, scalable, and fault-tolerant messaging system that decouples data producers from consumers, enabling asynchronous data processing.

## Features
- Highly available Kafka cluster with Zookeeper coordination
- Pre-configured topics for stock prices, market trends, and trading alerts
- Kafka UI for monitoring and management
- Persistent volume storage for data durability
- Health checks for service reliability

## Components
1. **Apache Kafka**: Distributed event streaming platform
2. **Zookeeper**: Coordination service for Kafka
3. **Kafka UI**: Web interface for Kafka management

## Topics
- `stock_prices`: Real-time stock price data (3 partitions)
- `market_trends`: Aggregated market trend data (1 partition)
- `trading_alerts`: Real-time trading signals (2 partitions)

## Configuration
The Kafka broker is configured with:
- Replication factor: 1 (for development; increase for production)
- Auto topic creation: Enabled
- Topic deletion: Enabled
- Retention periods: 7 days for stock data, 1 day for alerts

## Usage
1. Start the Kafka cluster:
   ```
   docker-compose up -d
   ```

2. Access Kafka UI:
   ```
   http://localhost:8080
   ```

3. Create additional topics:
   ```
   docker exec -it kafka kafka-topics --create --bootstrap-server kafka:9092 --topic new_topic --partitions 1 --replication-factor 1
   ```

4. List topics:
   ```
   docker exec -it kafka kafka-topics --list --bootstrap-server kafka:9092
   ```

## Data Flow
1. Producer services publish messages to Kafka topics
2. Messages are stored in Kafka with configured retention
3. Consumer services subscribe to topics and process messages

## Scaling
- Increase partitions for higher throughput
- Add more brokers for better fault tolerance
- Adjust retention settings based on storage requirements

## Monitoring
Use Kafka UI to monitor:
- Topic throughput and lag
- Consumer group status
- Broker health
- Message inspection
