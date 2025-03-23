import logging
import json
import time
import pandas as pd
from kafka import KafkaConsumer
from psycopg2.extras import execute_batch
from datetime import datetime
import psycopg2
import config
from indicators import add_scalping_indicators

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('db-writer')

class DatabaseWriter:
    """Writes stock market data from Kafka to PostgreSQL."""

    def __init__(self):
        self.connect_to_kafka()
        self.connect_to_database()
        self.create_tables_if_not_exist()
        self.batch_size = config.BATCH_SIZE
        self.batch_timeout = config.BATCH_TIMEOUT
        self.stock_data_batch = []
        self.last_commit_time = time.time()
        logger.info("Database writer initialized")

    def connect_to_kafka(self):
        try:
            self.consumer = KafkaConsumer(
                *config.KAFKA_TOPICS,
                bootstrap_servers=config.KAFKA_BROKER,
                auto_offset_reset='earliest',
                value_deserializer=lambda x: json.loads(x.decode('utf-8')),
                group_id=config.KAFKA_GROUP_ID
            )
            logger.info(f"Connected to Kafka broker at {config.KAFKA_BROKER}")
        except Exception as e:
            logger.error(f"Failed to connect to Kafka: {e}")
            raise

    def connect_to_database(self):
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
        try:
            cursor = self.conn.cursor()
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS stock_prices (
                    id SERIAL PRIMARY KEY,
                    symbol VARCHAR(10) NOT NULL,
                    price NUMERIC(10, 2) NOT NULL,
                    volume NUMERIC(20, 2),
                    timestamp TIMESTAMP NOT NULL,
                    fetch_timestamp BIGINT,
                    rsi NUMERIC(10,4),
                    ema_5 NUMERIC(10,4),
                    ema_9 NUMERIC(10,4),
                    macd NUMERIC(10,4),
                    macd_signal NUMERIC(10,4),
                    atr NUMERIC(10,4),
                    bb_upper NUMERIC(10,4),
                    bb_lower NUMERIC(10,4),
                    obv NUMERIC(20,4)
                );

                CREATE INDEX IF NOT EXISTS idx_stock_prices_symbol ON stock_prices(symbol);
                CREATE INDEX IF NOT EXISTS idx_stock_prices_timestamp ON stock_prices(timestamp);
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
        try:
            data = message.value
            df = pd.DataFrame([data])
            df = add_scalping_indicators(df)
            enriched = df.iloc[0]

            self.stock_data_batch.append((
                enriched.get('symbol'),
                enriched.get('close'),
                enriched.get('volume'),
                enriched.get('timestamp'),
                enriched.get('fetch_timestamp', int(time.time())),
                enriched.get('RSI'),
                enriched.get('EMA_5'),
                enriched.get('EMA_9'),
                enriched.get('MACD'),
                enriched.get('MACD_signal'),
                enriched.get('ATR'),
                enriched.get('BB_upper'),
                enriched.get('BB_lower'),
                enriched.get('OBV')
            ))

            current_time = time.time()
            if (len(self.stock_data_batch) >= self.batch_size or 
                current_time - self.last_commit_time >= self.batch_timeout):
                self.commit_batch()

        except Exception as e:
            logger.error(f"Error processing message: {e}")

    def commit_batch(self):
        if not self.stock_data_batch:
            return

        try:
            cursor = self.conn.cursor()
            execute_batch(cursor, """
                INSERT INTO stock_prices (
                    symbol, price, volume, timestamp, fetch_timestamp,
                    rsi, ema_5, ema_9, macd, macd_signal,
                    atr, bb_upper, bb_lower, obv
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """, self.stock_data_batch)

            self.conn.commit()
            logger.info(f"Committed batch of {len(self.stock_data_batch)} records to database")
            self.stock_data_batch = []
            self.last_commit_time = time.time()

        except Exception as e:
            self.conn.rollback()
            logger.error(f"Error committing batch to database: {e}")
        finally:
            cursor.close()

    def run(self):
        logger.info("Starting database writer")

        try:
            for message in self.consumer:
                self.process_message(message)

        except KeyboardInterrupt:
            logger.info("Database writer stopped by user")
        except Exception as e:
            logger.error(f"Error in database writer: {e}")
        finally:
            if self.stock_data_batch:
                self.commit_batch()
            if hasattr(self, 'consumer'):
                self.consumer.close()
                logger.info("Kafka consumer closed")
            if hasattr(self, 'conn'):
                self.conn.close()
                logger.info("Database connection closed")

if __name__ == "__main__":
    writer = DatabaseWriter()
    writer.run()
