#!/usr/bin/env python3
"""
Batch Processor for Stock Market Data Engineering Project
Processes stock data in scheduled batches for analysis and aggregation.
"""

import logging
import datetime
from pyspark.sql import SparkSession
from pyspark.sql.functions import col, avg, max, min, sum, count, date_format, window
from pyspark.sql.types import DoubleType
import config

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('batch-processor')

def create_spark_session():
    """Create and return a Spark session for batch processing."""
    return (SparkSession.builder
            .appName("StockDataBatchProcessor")
            .config("spark.jars.packages", "org.postgresql:postgresql:42.5.1")
            .getOrCreate())

def load_data_from_postgres(spark):
    """Load stock data from PostgreSQL database."""
    logger.info("Loading data from PostgreSQL")
    
    jdbc_url = f"jdbc:postgresql://{config.DB_HOST}:{config.DB_PORT}/{config.DB_NAME}"
    
    return (spark.read
            .format("jdbc")
            .option("url", jdbc_url)
            .option("dbtable", config.SOURCE_TABLE)
            .option("user", config.DB_USER)
            .option("password", config.DB_PASSWORD)
            .load())

def clean_data(df):
    """Clean and prepare data for processing."""
    logger.info("Cleaning and preparing data")
    
    # Import data_cleaner module for advanced cleaning
    from data_cleaner import remove_outliers, fill_missing_values
    
    # Basic cleaning
    cleaned_df = df.dropDuplicates()
    
    # Convert price to double if needed
    cleaned_df = cleaned_df.withColumn("price", col("price").cast(DoubleType()))
    
    # Apply advanced cleaning functions
    cleaned_df = remove_outliers(cleaned_df, "price")
    cleaned_df = fill_missing_values(cleaned_df)
    
    return cleaned_df

def aggregate_data(df):
    """Perform aggregations on the data."""
    logger.info("Performing data aggregations")
    
    # Import aggregation module for specific aggregations
    from aggregation import calculate_moving_averages, detect_trends
    
    # Daily aggregation
    daily_agg = df.groupBy(
        date_format(col("timestamp"), "yyyy-MM-dd").alias("date"),
        col("symbol")
    ).agg(
        avg("price").alias("avg_price"),
        max("price").alias("max_price"),
        min("price").alias("min_price"),
        sum("volume").alias("total_volume"),
        count("*").alias("data_points")
    )
    
    # Weekly aggregation
    weekly_agg = df.groupBy(
        date_format(col("timestamp"), "yyyy-ww").alias("year_week"),
        col("symbol")
    ).agg(
        avg("price").alias("avg_price"),
        max("price").alias("max_price"),
        min("price").alias("min_price"),
        sum("volume").alias("total_volume"),
        count("*").alias("data_points")
    )
    
    # Monthly aggregation
    monthly_agg = df.groupBy(
        date_format(col("timestamp"), "yyyy-MM").alias("year_month"),
        col("symbol")
    ).agg(
        avg("price").alias("avg_price"),
        max("price").alias("max_price"),
        min("price").alias("min_price"),
        sum("volume").alias("total_volume"),
        count("*").alias("data_points")
    )
    
    # Apply advanced aggregations
    daily_agg = calculate_moving_averages(daily_agg)
    daily_agg = detect_trends(daily_agg)
    
    return {
        "daily": daily_agg,
        "weekly": weekly_agg,
        "monthly": monthly_agg
    }

def save_to_postgres(df_dict):
    """Save aggregated data to PostgreSQL."""
    logger.info("Saving aggregated data to PostgreSQL")
    
    jdbc_url = f"jdbc:postgresql://{config.DB_HOST}:{config.DB_PORT}/{config.DB_NAME}"
    
    # Save daily aggregations
    df_dict["daily"].write \
        .format("jdbc") \
        .option("url", jdbc_url) \
        .option("dbtable", config.DAILY_AGG_TABLE) \
        .option("user", config.DB_USER) \
        .option("password", config.DB_PASSWORD) \
        .mode("append") \
        .save()
    
    # Save weekly aggregations
    df_dict["weekly"].write \
        .format("jdbc") \
        .option("url", jdbc_url) \
        .option("dbtable", config.WEEKLY_AGG_TABLE) \
        .option("user", config.DB_USER) \
        .option("password", config.DB_PASSWORD) \
        .mode("append") \
        .save()
    
    # Save monthly aggregations
    df_dict["monthly"].write \
        .format("jdbc") \
        .option("url", jdbc_url) \
        .option("dbtable", config.MONTHLY_AGG_TABLE) \
        .option("user", config.DB_USER) \
        .option("password", config.DB_PASSWORD) \
        .mode("append") \
        .save()
    
    logger.info("All aggregated data saved successfully")

def main():
    """Main function to run the batch processor."""
    logger.info("Starting Stock Market Data Batch Processor")
    start_time = datetime.datetime.now()
    
    try:
        # Create Spark session
        spark = create_spark_session()
        logger.info("Created Spark session")
        
        # Load data from PostgreSQL
        df = load_data_from_postgres(spark)
        logger.info(f"Loaded {df.count()} records from PostgreSQL")
        
        # Clean data
        cleaned_df = clean_data(df)
        logger.info(f"Cleaned data: {cleaned_df.count()} records remaining")
        
        # Aggregate data
        aggregated_data = aggregate_data(cleaned_df)
        logger.info("Data aggregation completed")
        
        # Save aggregated data to PostgreSQL
        save_to_postgres(aggregated_data)
        
        end_time = datetime.datetime.now()
        duration = (end_time - start_time).total_seconds()
        logger.info(f"Batch processing completed in {duration} seconds")
        
    except Exception as e:
        logger.error(f"Error in batch processing: {e}")
    finally:
        if 'spark' in locals():
            spark.stop()
            logger.info("Spark session stopped")

if __name__ == "__main__":
    main()
