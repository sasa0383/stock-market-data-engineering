#!/usr/bin/env python3
"""
Producer Service for Stock Market Data Engineering Project
Fetches real-time stock data from an API and pushes it to Kafka.
"""

import json
import time
import logging
import requests
from kafka import KafkaProducer
from config import API_KEY, API_URL_TEMPLATE, KAFKA_BROKER, TOPIC, FETCH_INTERVAL, SYMBOLS

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('producer-service')

def create_kafka_producer():
    """Create and return a Kafka producer instance."""
    try:
        producer = KafkaProducer(
            bootstrap_servers=KAFKA_BROKER,
            value_serializer=lambda x: json.dumps(x).encode('utf-8'),
            acks='all',  # Wait for all replicas to acknowledge
            retries=3,   # Retry sending on failure
        )
        logger.info(f"Connected to Kafka broker at {KAFKA_BROKER}")
        return producer
    except Exception as e:
        logger.error(f"Failed to connect to Kafka broker: {e}")
        raise

def fetch_stock_data(symbol):
    """Fetch stock data for a given symbol from the API."""
    try:
        url = API_URL_TEMPLATE.format(symbol=symbol, api_key=API_KEY)
        response = requests.get(url, timeout=10)
        response.raise_for_status()  # Raise exception for HTTP errors
        
        data = response.json()
        if not data:
            logger.warning(f"No data returned for symbol {symbol}")
            return None
            
        # Add timestamp for when we received the data
        data['fetch_timestamp'] = int(time.time())
        logger.info(f"Successfully fetched data for {symbol}")
        return data
    except requests.exceptions.RequestException as e:
        logger.error(f"Error fetching data for {symbol}: {e}")
        return None

def main():
    """Main function to run the producer service."""
    logger.info("Starting Stock Market Data Producer Service")
    
    try:
        producer = create_kafka_producer()
        
        while True:
            for symbol in SYMBOLS:
                stock_data = fetch_stock_data(symbol)
                
                if stock_data:
                    # Send stock data to Kafka
                    producer.send(TOPIC, value=stock_data)
                    logger.info(f"Published data for {symbol} to topic {TOPIC}")
                
            # Flush to ensure all messages are sent
            producer.flush()
            logger.info(f"Sleeping for {FETCH_INTERVAL} seconds")
            time.sleep(FETCH_INTERVAL)
            
    except KeyboardInterrupt:
        logger.info("Producer service stopped by user")
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
    finally:
        if 'producer' in locals():
            producer.close()
            logger.info("Kafka producer closed")

if __name__ == "__main__":
    main()
