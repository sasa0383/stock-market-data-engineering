#!/usr/bin/env python3
"""
Batch Processor for Stock Market Data Engineering Project
Processes stock data in batches using Apache Spark
"""

import logging
from datetime import datetime, timedelta
from pyspark.sql import SparkSession
from pyspark.sql.functions import col, avg, max, min, sum, datediff, window
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
            .appName("StockBatchProcessor")
            .config("spark.jars.packages", "org.postgresql:postgresql:42.5.1")
            .getOrCreate())

def read_from_postgres(spark):
    """Read stock data from PostgreSQL"""
    logger.info("Reading stock data from PostgreSQL")
    return (spark.read
            .format("jdbc")
            .option("url", config.POSTGRES_URL)
            .option("dbtable", "stock_prices")
            .option("user", config.POSTGRES_USER)
            .option("password", config.POSTGRES_PASSWORD)
            .load())

def process_daily_aggregation(df):
    """Process daily aggregation of stock data"""
    logger.info("Processing daily aggregation")
    return (df.groupBy("symbol", "date")
            .agg(
                avg("open").alias("avg_open"),
                avg("close").alias("avg_close"),
                max("high").alias("max_high"),
                min("low").alias("min_low"),
                sum("volume").alias("total_volume")
            ))

def process_weekly_aggregation(df):
    """Process weekly aggregation of stock data"""
    logger.info("Processing weekly aggregation")
    return (df.groupBy("symbol", window("date", "1 week"))
            .agg(
                avg("close").alias("avg_close"),
                max("high").alias("max_high"),
                min("low").alias("min_low"),
                sum("volume").alias("total_volume")
            ))

def process_monthly_aggregation(df):
    """Process monthly aggregation of stock data"""
    logger.info("Processing monthly aggregation")
    return (df.groupBy("symbol", window("date", "1 month"))
            .agg(
                avg("close").alias("avg_close"),
                max("high").alias("max_high"),
                min("low").alias("min_low"),
                sum("volume").alias("total_volume")
            ))

def calculate_moving_averages(df):
    """Calculate moving averages for stock prices"""
    logger.info("Calculating moving averages")
    
    # Calculate 7-day moving average
    df_7day = df.groupBy("symbol").agg(
        avg(col("close").over(
            window("date", "7 days").orderBy("date")
        )).alias("ma_7day")
    )
    
    # Calculate 30-day moving average
    df_30day = df.groupBy("symbol").agg(
        avg(col("close").over(
            window("date", "30 days").orderBy("date")
        )).alias("ma_30day")
    )
    
    # Calculate 90-day moving average
    df_90day = df.groupBy("symbol").agg(
        avg(col("close").over(
            window("date", "90 days").orderBy("date")
        )).alias("ma_90day")
    )
    
    return df_7day.join(df_30day, "symbol").join(df_90day, "symbol")

def write_to_postgres(df, table_name):
    """Write processed data to PostgreSQL"""
    logger.info(f"Writing processed data to {table_name}")
    (df.write
     .format("jdbc")
     .option("url", config.POSTGRES_URL)
     .option("dbtable", table_name)
     .option("user", config.POSTGRES_USER)
     .option("password", config.POSTGRES_PASSWORD)
     .mode("overwrite")
     .save())

def main():
    """Main function to process stock data in batches"""
    logger.info("Starting Stock Market Batch Processor")
    
    # Create Spark session
    spark = create_spark_session()
    
    try:
        # Read data from PostgreSQL
        stock_df = read_from_postgres(spark)
        
        # Process daily aggregation
        daily_agg = process_daily_aggregation(stock_df)
        write_to_postgres(daily_agg, "stock_daily_aggregates")
        
        # Process weekly aggregation
        weekly_agg = process_weekly_aggregation(stock_df)
        write_to_postgres(weekly_agg, "stock_weekly_aggregates")
        
        # Process monthly aggregation
        monthly_agg = process_monthly_aggregation(stock_df)
        write_to_postgres(monthly_agg, "stock_monthly_aggregates")
        
        # Calculate moving averages
        moving_avgs = calculate_moving_averages(stock_df)
        write_to_postgres(moving_avgs, "stock_moving_averages")
        
        logger.info("Batch processing completed successfully")
    except Exception as e:
        logger.error(f"Error in batch processing: {e}")
    finally:
        spark.stop()
        logger.info("Spark session stopped")

if __name__ == "__main__":
    main()
