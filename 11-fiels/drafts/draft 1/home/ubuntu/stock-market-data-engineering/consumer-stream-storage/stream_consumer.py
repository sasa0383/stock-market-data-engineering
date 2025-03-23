#!/usr/bin/env python3
"""
Stream Consumer for Stock Market Data Engineering Project
Consumes real-time stock data from Kafka and processes it using Spark Streaming
"""

import json
import logging
from pyspark.sql import SparkSession
from pyspark.sql.functions import col, window, avg, max, min, expr
from pyspark.sql.types import StructType, StructField, StringType, DoubleType, TimestampType, LongType
import config

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def create_spark_session():
    """Create and return a Spark session"""
    return (SparkSession.builder
            .appName("StockStreamProcessor")
            .config("spark.sql.streaming.checkpointLocation", "/tmp/checkpoint")
            .config("spark.jars.packages", "org.apache.spark:spark-sql-kafka-0-10_2.12:3.3.0")
            .getOrCreate())

def define_schema():
    """Define the schema for stock data"""
    return StructType([
        StructField("symbol", StringType(), True),
        StructField("timestamp", LongType(), True),
        StructField("datetime", TimestampType(), True),
        StructField("open", DoubleType(), True),
        StructField("high", DoubleType(), True),
        StructField("low", DoubleType(), True),
        StructField("close", DoubleType(), True),
        StructField("volume", LongType(), True)
    ])

def read_from_kafka(spark):
    """Read streaming data from Kafka"""
    return (spark
            .readStream
            .format("kafka")
            .option("kafka.bootstrap.servers", config.KAFKA_BROKER)
            .option("subscribe", config.KAFKA_TOPIC_STOCK_PRICES)
            .option("startingOffsets", "latest")
            .load())

def process_stream(df, schema):
    """Process the streaming data"""
    # Parse JSON data
    parsed_df = df.selectExpr("CAST(value AS STRING)") \
        .select(expr("from_json(value, '{schema}') as data").format(schema=schema)) \
        .select("data.*")
    
    # Convert timestamp to timestamp type
    parsed_df = parsed_df.withColumn("datetime", 
                                    expr("to_timestamp(datetime)"))
    
    # Calculate 5-minute moving averages
    window_avg = parsed_df \
        .withWatermark("datetime", "10 minutes") \
        .groupBy(
            col("symbol"),
            window(col("datetime"), "5 minutes")
        ) \
        .agg(
            avg("close").alias("avg_price"),
            max("high").alias("max_price"),
            min("low").alias("min_price"),
            avg("volume").alias("avg_volume")
        )
    
    return window_avg

def write_to_console(df):
    """Write the processed data to console (for development)"""
    return (df.writeStream
            .outputMode("update")
            .format("console")
            .option("truncate", False)
            .start())

def write_to_postgres(df):
    """Write the processed data to PostgreSQL"""
    return (df.writeStream
            .foreachBatch(lambda batch_df, batch_id: batch_df.write
                         .format("jdbc")
                         .option("url", config.POSTGRES_URL)
                         .option("dbtable", "stock_aggregates")
                         .option("user", config.POSTGRES_USER)
                         .option("password", config.POSTGRES_PASSWORD)
                         .mode("append")
                         .save())
            .outputMode("update")
            .start())

def main():
    """Main function to process streaming stock data"""
    logger.info("Starting Stock Market Stream Consumer")
    
    # Create Spark session
    spark = create_spark_session()
    
    # Define schema
    schema = define_schema()
    
    # Read from Kafka
    kafka_df = read_from_kafka(spark)
    
    # Process stream
    processed_df = process_stream(kafka_df, schema)
    
    # Write to outputs
    if config.WRITE_TO_CONSOLE:
        console_query = write_to_console(processed_df)
    
    if config.WRITE_TO_POSTGRES:
        postgres_query = write_to_postgres(processed_df)
    
    # Wait for termination
    spark.streams.awaitAnyTermination()

if __name__ == "__main__":
    main()
