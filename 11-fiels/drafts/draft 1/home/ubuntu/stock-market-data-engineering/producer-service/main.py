#!/usr/bin/env python3
"""
Producer Service for Stock Market Data Engineering Project
Fetches real-time stock data from Yahoo Finance API and pushes to Kafka
"""

import json
import time
import logging
import sys
from datetime import datetime
import requests
from kafka import KafkaProducer
import config

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def create_kafka_producer():
    """Create and return a Kafka producer instance"""
    try:
        producer = KafkaProducer(
            bootstrap_servers=config.KAFKA_BROKER,
            value_serializer=lambda x: json.dumps(x).encode('utf-8'),
            acks='all',  # Wait for all replicas to acknowledge
            retries=3,   # Retry sending on failure
            linger_ms=5  # Small delay to batch messages
        )
        logger.info(f"Connected to Kafka broker at {config.KAFKA_BROKER}")
        return producer
    except Exception as e:
        logger.error(f"Failed to create Kafka producer: {e}")
        sys.exit(1)

def fetch_stock_data(symbol):
    """Fetch stock data from Yahoo Finance API"""
    try:
        # Using Yahoo Finance API
        url = f"https://query1.finance.yahoo.com/v8/finance/chart/{symbol}"
        params = {
            "interval": "1d",
            "range": "1d"
        }
        headers = {
            "User-Agent": "Mozilla/5.0"
        }
        
        response = requests.get(url, params=params, headers=headers)
        response.raise_for_status()
        
        data = response.json()
        
        # Extract relevant data
        timestamp = data["chart"]["result"][0]["timestamp"][0]
        quote = data["chart"]["result"][0]["indicators"]["quote"][0]
        
        stock_data = {
            "symbol": symbol,
            "timestamp": timestamp,
            "datetime": datetime.fromtimestamp(timestamp).isoformat(),
            "open": quote["open"][0],
            "high": quote["high"][0],
            "low": quote["low"][0],
            "close": quote["close"][0],
            "volume": quote["volume"][0]
        }
        
        logger.info(f"Successfully fetched data for {symbol}")
        return stock_data
    except requests.exceptions.RequestException as e:
        logger.error(f"API request failed for {symbol}: {e}")
        return None
    except (KeyError, IndexError) as e:
        logger.error(f"Failed to parse data for {symbol}: {e}")
        return None
    except Exception as e:
        logger.error(f"Unexpected error fetching data for {symbol}: {e}")
        return None

def publish_to_kafka(producer, topic, data):
    """Publish data to Kafka topic"""
    try:
        future = producer.send(topic, value=data)
        # Block until message is sent (or timeout)
        record_metadata = future.get(timeout=10)
        logger.info(f"Published to {topic}: {data['symbol']} at offset {record_metadata.offset}")
        return True
    except Exception as e:
        logger.error(f"Failed to publish to Kafka: {e}")
        return False

def main():
    """Main function to fetch stock data and publish to Kafka"""
    logger.info("Starting Stock Market Data Producer Service")
    
    # Create Kafka producer
    producer = create_kafka_producer()
    
    try:
        while True:
            for symbol in config.STOCK_SYMBOLS:
                stock_data = fetch_stock_data(symbol)
                if stock_data:
                    publish_to_kafka(producer, config.KAFKA_TOPIC_STOCK_PRICES, stock_data)
            
            logger.info(f"Sleeping for {config.FETCH_INTERVAL} seconds")
            time.sleep(config.FETCH_INTERVAL)
    except KeyboardInterrupt:
        logger.info("Producer service stopped by user")
    finally:
        if producer:
            producer.flush()  # Make sure all messages are sent
            producer.close()
            logger.info("Kafka producer closed")

if __name__ == "__main__":
    main()
