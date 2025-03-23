#!/usr/bin/env python3
"""
DB Writer for Stock Market Data Engineering Project
Consumes data from Kafka and writes to PostgreSQL/MongoDB
"""

import logging
import json
import time
from datetime import datetime
import psycopg2
from psycopg2.extras import execute_values
from kafka import KafkaConsumer
import config

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def connect_to_kafka():
    """Connect to Kafka broker and return consumer"""
    try:
        consumer = KafkaConsumer(
            config.KAFKA_TOPIC_STOCK_PRICES,
            bootstrap_servers=config.KAFKA_BROKER,
            value_deserializer=lambda x: json.loads(x.decode('utf-8')),
            auto_offset_reset='earliest',
            group_id='db-writer'
        )
        logger.info(f"Connected to Kafka broker at {config.KAFKA_BROKER}")
        return consumer
    except Exception as e:
        logger.error(f"Failed to connect to Kafka: {e}")
        raise

def connect_to_postgres():
    """Connect to PostgreSQL database and return connection"""
    try:
        conn = psycopg2.connect(
            host=config.POSTGRES_HOST,
            database=config.POSTGRES_DB,
            user=config.POSTGRES_USER,
            password=config.POSTGRES_PASSWORD
        )
        logger.info(f"Connected to PostgreSQL database at {config.POSTGRES_HOST}")
        return conn
    except Exception as e:
        logger.error(f"Failed to connect to PostgreSQL: {e}")
        raise

def create_tables(conn):
    """Create necessary tables if they don't exist"""
    try:
        with conn.cursor() as cur:
            # Create stock_prices table
            cur.execute("""
                CREATE TABLE IF NOT EXISTS stock_prices (
                    id SERIAL PRIMARY KEY,
                    symbol VARCHAR(10) NOT NULL,
                    timestamp BIGINT NOT NULL,
                    date TIMESTAMP NOT NULL,
                    open NUMERIC(10, 2) NOT NULL,
                    high NUMERIC(10, 2) NOT NULL,
                    low NUMERIC(10, 2) NOT NULL,
                    close NUMERIC(10, 2) NOT NULL,
                    volume BIGINT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Create index on symbol and date
            cur.execute("""
                CREATE INDEX IF NOT EXISTS idx_stock_prices_symbol_date
                ON stock_prices (symbol, date)
            """)
            
            # Create trading_signals table
            cur.execute("""
                CREATE TABLE IF NOT EXISTS trading_signals (
                    id SERIAL PRIMARY KEY,
                    timestamp TIMESTAMP NOT NULL,
                    symbol VARCHAR(10) NOT NULL,
                    action VARCHAR(10) NOT NULL,
                    price NUMERIC(10, 2) NOT NULL,
                    quantity INTEGER NOT NULL,
                    details JSONB,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            conn.commit()
            logger.info("Database tables created successfully")
    except Exception as e:
        logger.error(f"Error creating tables: {e}")
        conn.rollback()
        raise

def batch_insert_to_postgres(conn, records, table_name):
    """Insert batch of records to PostgreSQL"""
    if not records:
        return
    
    try:
        with conn.cursor() as cur:
            if table_name == 'stock_prices':
                query = """
                    INSERT INTO stock_prices 
                    (symbol, timestamp, date, open, high, low, close, volume)
                    VALUES %s
                    ON CONFLICT (symbol, date) DO UPDATE SET
                    open = EXCLUDED.open,
                    high = EXCLUDED.high,
                    low = EXCLUDED.low,
                    close = EXCLUDED.close,
                    volume = EXCLUDED.volume
                """
                values = [(
                    r['symbol'],
                    r['timestamp'],
                    datetime.fromtimestamp(r['timestamp']),
                    r['open'],
                    r['high'],
                    r['low'],
                    r['close'],
                    r['volume']
                ) for r in records]
            else:
                logger.warning(f"Unknown table name: {table_name}")
                return
            
            execute_values(cur, query, values)
            conn.commit()
            logger.info(f"Inserted {len(records)} records into {table_name}")
    except Exception as e:
        logger.error(f"Error inserting records to {table_name}: {e}")
        conn.rollback()

def process_messages(consumer, conn):
    """Process messages from Kafka and write to PostgreSQL"""
    batch_size = config.BATCH_SIZE
    batch_timeout = config.BATCH_TIMEOUT
    records = []
    last_commit_time = time.time()
    
    try:
        for message in consumer:
            stock_data = message.value
            records.append(stock_data)
            
            # Commit when batch size is reached or timeout occurs
            current_time = time.time()
            if len(records) >= batch_size or (current_time - last_commit_time) >= batch_timeout:
                batch_insert_to_postgres(conn, records, 'stock_prices')
                records = []
                last_commit_time = current_time
    except KeyboardInterrupt:
        logger.info("Process interrupted by user")
    except Exception as e:
        logger.error(f"Error processing messages: {e}")
    finally:
        # Insert any remaining records
        if records:
            batch_insert_to_postgres(conn, records, 'stock_prices')

def main():
    """Main function to run the DB writer"""
    logger.info("Starting Stock Market DB Writer")
    
    try:
        # Connect to Kafka
        consumer = connect_to_kafka()
        
        # Connect to PostgreSQL
        conn = connect_to_postgres()
        
        # Create tables if they don't exist
        create_tables(conn)
        
        # Process messages
        process_messages(consumer, conn)
    except Exception as e:
        logger.error(f"Error in DB writer: {e}")
    finally:
        if 'conn' in locals() and conn:
            conn.close()
            logger.info("PostgreSQL connection closed")
        logger.info("DB writer stopped")

if __name__ == "__main__":
    main()
