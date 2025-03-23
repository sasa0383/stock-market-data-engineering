#!/usr/bin/env python3
"""
Database Writer for Stock Market Data Engineering Project
Writes Kafka stream to PostgreSQL or MongoDB.
"""

import logging
import json
import time
from kafka import KafkaConsumer
import psycopg2
from psycopg2.extras import execute_batch
from datetime import datetime
import config

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('db-writer')

class DatabaseWriter:
    """Writes stock market data from Kafka to PostgreSQL."""
    
    def __init__(self):
        """Initialize the database writer."""
        self.connect_to_kafka()
        self.connect_to_database()
        self.create_tables_if_not_exist()
        self.batch_size = config.BATCH_SIZE
        self.batch_timeout = config.BATCH_TIMEOUT
        self.stock_data_batch = []
        self.last_commit_time = time.time()
        
        logger.info("Database writer initialized")
    
    def connect_to_kafka(self):
        """Connect to Kafka broker and subscribe to topics."""
        try:
            self.consumer = KafkaConsumer(
                config.STOCK_PRICES_TOPIC,
                bootstrap_servers=config.KAFKA_BROKER,
                auto_offset_reset='earliest',
                value_deserializer=lambda x: json.loads(x.decode('utf-8')),
                group_id='db-writer-group'
            )
            logger.info(f"Connected to Kafka broker at {config.KAFKA_BROKER}")
        except Exception as e:
            logger.error(f"Failed to connect to Kafka: {e}")
            raise
    
    def connect_to_database(self):
        """Connect to PostgreSQL database."""
        try:
            self.conn = psycopg2.connect(
                host=config.DB_HOST,
                port=config.DB_PORT,
                dbname=config.DB_NAME,
                user=config.DB_USER,
                password=config.DB_PASSWORD
            )
            self.conn.autocommit = False
            logger.info(f"Connected to PostgreSQL database at {config.DB_HOST}")
        except Exception as e:
            logger.error(f"Failed to connect to database: {e}")
            raise
    
    def create_tables_if_not_exist(self):
        """Create database tables if they don't exist."""
        try:
            cursor = self.conn.cursor()
            
            # Create stock_prices table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS stock_prices (
                    id SERIAL PRIMARY KEY,
                    symbol VARCHAR(10) NOT NULL,
                    price NUMERIC(10, 2) NOT NULL,
                    volume NUMERIC(20, 2),
                    timestamp TIMESTAMP NOT NULL,
                    fetch_timestamp BIGINT
                );
                
                CREATE INDEX IF NOT EXISTS idx_stock_prices_symbol ON stock_prices(symbol);
                CREATE INDEX IF NOT EXISTS idx_stock_prices_timestamp ON stock_prices(timestamp);
            """)
            
            # Create stock_metrics table for stream processing results
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS stock_metrics (
                    id SERIAL PRIMARY KEY,
                    symbol VARCHAR(10) NOT NULL,
                    window_start TIMESTAMP NOT NULL,
                    window_end TIMESTAMP NOT NULL,
                    avg_price NUMERIC(10, 2),
                    max_price NUMERIC(10, 2),
                    min_price NUMERIC(10, 2),
                    avg_volume NUMERIC(20, 2),
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );
                
                CREATE INDEX IF NOT EXISTS idx_stock_metrics_symbol ON stock_metrics(symbol);
                CREATE INDEX IF NOT EXISTS idx_stock_metrics_window ON stock_metrics(window_start, window_end);
            """)
            
            self.conn.commit()
            logger.info("Database tables created or already exist")
        except Exception as e:
            self.conn.rollback()
            logger.error(f"Error creating tables: {e}")
            raise
        finally:
            cursor.close()
    
    def process_message(self, message):
        """Process incoming Kafka message and add to batch."""
        try:
            data = message.value
            
            # Extract fields
            symbol = data.get('symbol')
            price = data.get('price')
            volume = data.get('volume', 0)
            
            # Handle timestamp
            if 'timestamp' in data:
                # If timestamp is provided as ISO format string
                if isinstance(data['timestamp'], str):
                    timestamp = data['timestamp']
                # If timestamp is provided as epoch seconds
                elif isinstance(data['timestamp'], (int, float)):
                    timestamp = datetime.fromtimestamp(data['timestamp']).isoformat()
                else:
                    timestamp = datetime.now().isoformat()
            else:
                timestamp = datetime.now().isoformat()
            
            fetch_timestamp = data.get('fetch_timestamp', int(time.time()))
            
            # Add to batch
            self.stock_data_batch.append((
                symbol,
                price,
                volume,
                timestamp,
                fetch_timestamp
            ))
            
            # Check if batch should be committed
            current_time = time.time()
            if (len(self.stock_data_batch) >= self.batch_size or 
                current_time - self.last_commit_time >= self.batch_timeout):
                self.commit_batch()
                
        except Exception as e:
            logger.error(f"Error processing message: {e}")
    
    def commit_batch(self):
        """Commit batch of stock data to database."""
        if not self.stock_data_batch:
            return
            
        try:
            cursor = self.conn.cursor()
            
            # Insert batch of stock data
            execute_batch(cursor, """
                INSERT INTO stock_prices (symbol, price, volume, timestamp, fetch_timestamp)
                VALUES (%s, %s, %s, %s, %s)
            """, self.stock_data_batch)
            
            self.conn.commit()
            logger.info(f"Committed batch of {len(self.stock_data_batch)} records to database")
            
            # Reset batch
            self.stock_data_batch = []
            self.last_commit_time = time.time()
            
        except Exception as e:
            self.conn.rollback()
            logger.error(f"Error committing batch to database: {e}")
        finally:
            cursor.close()
    
    def run(self):
        """Main loop to process messages and write to database."""
        logger.info("Starting database writer")
        
        try:
            # Process Kafka messages
            for message in self.consumer:
                self.process_message(message)
                
        except KeyboardInterrupt:
            logger.info("Database writer stopped by user")
        except Exception as e:
            logger.error(f"Error in database writer: {e}")
        finally:
            # Commit any remaining batch
            if self.stock_data_batch:
                self.commit_batch()
                
            # Close connections
            if hasattr(self, 'consumer'):
                self.consumer.close()
                logger.info("Kafka consumer closed")
                
            if hasattr(self, 'conn'):
                self.conn.close()
                logger.info("Database connection closed")

if __name__ == "__main__":
    writer = DatabaseWriter()
    writer.run()
