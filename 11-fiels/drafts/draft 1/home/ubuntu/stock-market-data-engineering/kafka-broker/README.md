# Kafka Broker

This component manages the Kafka message broker and Zookeeper for the stock market data engineering project.

## Overview

The Kafka broker serves as the central messaging system for the entire data pipeline, enabling:
- Decoupling of data producers from consumers
- Reliable message delivery with persistence
- Scalable data processing with multiple consumers
- Topic-based message organization

## Components

- **Apache Kafka**: Distributed event streaming platform
- **Zookeeper**: Coordination service for Kafka

## Configuration

The setup includes:
- 3 partitions per topic for parallelism
- Replication factor of 1 (for development; increase for production)
- Auto-creation of topics enabled
- Exposed ports for external access

## Kafka Topics

The following topics are created:
- `stock_prices`: Raw stock price data from the producer service
- `market_trends`: Processed market trend information
- `trading_signals`: Signals for potential trading actions

## Usage

### Starting the Kafka Broker

```bash
docker-compose up -d
```

### Creating Topics

The `kafka-config.sh` script automatically creates the required topics:

```bash
docker exec -it kafka /bin/bash /scripts/kafka-config.sh
```

### Monitoring Topics

List all topics:
```bash
docker exec -it kafka kafka-topics --list --bootstrap-server kafka:9092
```

Describe a topic:
```bash
docker exec -it kafka kafka-topics --describe --topic stock_prices --bootstrap-server kafka:9092
```

### Consuming Messages (for testing)

```bash
docker exec -it kafka kafka-console-consumer --bootstrap-server kafka:9092 --topic stock_prices --from-beginning
```
