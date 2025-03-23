#!/usr/bin/env python3
"""
Stream Consumer for Stock Market Data Engineering Project
Consumes real-time stock data from Kafka and processes it using Spark Streaming.
"""

import json
import logging
from pyspark.sql import SparkSession
from pyspark.sql.functions import from_json, col, window, avg, max, min, expr
from pyspark.sql.types import StructType, StructField, StringType, DoubleType, TimestampType, LongType

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('stream-consumer')

# Define schema for stock data
stock_schema = StructType([
    StructField("symbol", StringType(), True),
    StructField("price", DoubleType(), True),
    StructField("volume", DoubleType(), True),
    StructField("timestamp", TimestampType(), True),
    StructField("fetch_timestamp", LongType(), True)
])

def create_spark_session():
    """Create and return a Spark session configured for streaming."""
    return (SparkSession.builder
            .appName("StockDataStreamProcessor")
            .config("spark.sql.streaming.checkpointLocation", "/tmp/checkpoint")
            .config("spark.jars.packages", "org.apache.spark:spark-sql-kafka-0-10_2.12:3.3.0")
            .getOrCreate())

def read_from_kafka(spark):
    """Read streaming data from Kafka."""
    return (spark
            .readStream
            .format("kafka")
            .option("kafka.bootstrap.servers", "kafka:9092")
            .option("subscribe", "stock_prices")
            .option("startingOffsets", "latest")
            .load())

def process_stream(df):
    """Process the streaming data."""
    # Parse JSON data from Kafka
    parsed_df = df.selectExpr("CAST(value AS STRING)") \
        .select(from_json(col("value"), stock_schema).alias("data")) \
        .select("data.*")
    
    # Convert epoch timestamp to timestamp type
    parsed_df = parsed_df.withColumn(
        "event_time", 
        expr("CAST(from_unixtime(fetch_timestamp) AS TIMESTAMP)")
    )
    
    # Calculate real-time metrics with 5-minute windows
    windowed_stats = parsed_df \
        .withWatermark("event_time", "10 minutes") \
        .groupBy(
            col("symbol"),
            window(col("event_time"), "5 minutes")
        ) \
        .agg(
            avg("price").alias("avg_price"),
            max("price").alias("max_price"),
            min("price").alias("min_price"),
            avg("volume").alias("avg_volume")
        )
    
    return windowed_stats

def write_to_console(df):
    """Write streaming results to console (for development)."""
    return (df.writeStream
            .outputMode("complete")
            .format("console")
            .option("truncate", False)
            .start())

def write_to_postgres(df):
    """Write streaming results to PostgreSQL."""
    return (df.writeStream
            .foreachBatch(lambda batch_df, batch_id: batch_df.write
                         .format("jdbc")
                         .option("url", "jdbc:postgresql://postgres:5432/stockdata")
                         .option("dbtable", "stock_metrics")
                         .option("user", "postgres")
                         .option("password", "postgres")
                         .mode("append")
                         .save())
            .outputMode("update")
            .start())

def main():
    """Main function to run the stream consumer."""
    logger.info("Starting Stock Market Data Stream Consumer")
    
    try:
        # Create Spark session
        spark = create_spark_session()
        logger.info("Created Spark session")
        
        # Read from Kafka
        kafka_df = read_from_kafka(spark)
        logger.info("Connected to Kafka stream")
        
        # Process the stream
        processed_df = process_stream(kafka_df)
        logger.info("Processing stream with windowed aggregations")
        
        # Write to console for development/debugging
        console_query = write_to_console(processed_df)
        logger.info("Writing to console")
        
        # Write to PostgreSQL
        postgres_query = write_to_postgres(processed_df)
        logger.info("Writing to PostgreSQL")
        
        # Wait for termination
        spark.streams.awaitAnyTermination()
        
    except Exception as e:
        logger.error(f"Error in stream processing: {e}")
    finally:
        logger.info("Stream consumer stopped")

if __name__ == "__main__":
    main()
