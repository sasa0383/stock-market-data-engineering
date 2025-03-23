#!/usr/bin/env python3
"""
Data Cleaner for Stock Market Data Engineering Project
Cleans and preprocesses stock data for batch processing
"""

import logging
import pandas as pd
import numpy as np
from pyspark.sql import SparkSession
from pyspark.sql.functions import col, when, isnan, isnull

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def create_spark_session():
    """Create and return a Spark session"""
    return (SparkSession.builder
            .appName("StockDataCleaner")
            .getOrCreate())

def clean_stock_data(df):
    """Clean stock data by handling missing values and outliers"""
    logger.info("Cleaning stock data")
    
    # Count initial rows
    initial_count = df.count()
    logger.info(f"Initial row count: {initial_count}")
    
    # Handle missing values
    df_cleaned = df.na.fill({
        "open": None,
        "high": None,
        "low": None,
        "close": None,
        "volume": 0
    })
    
    # Fill missing price data with previous day's close when available
    # This is a simplified approach - in a real implementation, we would use window functions
    # to fill with the previous day's values
    
    # Remove rows with still-missing critical data
    df_cleaned = df_cleaned.filter(
        col("symbol").isNotNull() & 
        col("date").isNotNull() & 
        col("close").isNotNull()
    )
    
    # Handle outliers - filter out extreme price changes (e.g., > 20%)
    # This is a simplified approach - in a real implementation, we would use more sophisticated outlier detection
    df_cleaned = df_cleaned.filter(
        (col("high") / col("low") < 1.5)  # Extreme intraday volatility check
    )
    
    # Count final rows
    final_count = df_cleaned.count()
    logger.info(f"Final row count after cleaning: {final_count}")
    logger.info(f"Removed {initial_count - final_count} rows during cleaning")
    
    return df_cleaned

def validate_data(df):
    """Validate data quality after cleaning"""
    logger.info("Validating data quality")
    
    # Check for remaining null values
    null_counts = {col_name: df.filter(col(col_name).isNull()).count() 
                  for col_name in df.columns}
    logger.info(f"Null value counts: {null_counts}")
    
    # Check for logical consistency
    invalid_price_rows = df.filter(
        (col("low") > col("high")) | 
        (col("open") > col("high")) | 
        (col("open") < col("low")) | 
        (col("close") > col("high")) | 
        (col("close") < col("low"))
    ).count()
    logger.info(f"Rows with invalid price relationships: {invalid_price_rows}")
    
    # Check for negative values where inappropriate
    negative_price_rows = df.filter(
        (col("open") < 0) | 
        (col("high") < 0) | 
        (col("low") < 0) | 
        (col("close") < 0)
    ).count()
    logger.info(f"Rows with negative prices: {negative_price_rows}")
    
    negative_volume_rows = df.filter(col("volume") < 0).count()
    logger.info(f"Rows with negative volume: {negative_volume_rows}")
    
    return invalid_price_rows == 0 and negative_price_rows == 0 and negative_volume_rows == 0

def main():
    """Main function to clean stock data"""
    logger.info("Starting Stock Data Cleaner")
    
    # Create Spark session
    spark = create_spark_session()
    
    try:
        # Read data from source (this would typically be from a database or file)
        # For this example, we'll assume the data is already loaded in a DataFrame
        
        # In a real implementation, we would read from a source like:
        # df = spark.read.format("jdbc").option(...).load()
        
        # For demonstration, we'll create a sample DataFrame
        logger.info("Creating sample DataFrame for demonstration")
        sample_data = [
            ("AAPL", "2023-01-01", 150.0, 155.0, 148.0, 152.0, 1000000),
            ("AAPL", "2023-01-02", 152.0, 158.0, 151.0, 157.0, 1200000),
            ("AAPL", "2023-01-03", 157.0, 160.0, 155.0, 159.0, 1100000),
            ("AAPL", "2023-01-04", 159.0, 165.0, 158.0, 163.0, 1300000),
            ("AAPL", "2023-01-05", 163.0, 167.0, 162.0, 166.0, 1400000),
            # Add some problematic data
            ("AAPL", "2023-01-06", None, 170.0, 164.0, 168.0, 1500000),
            ("AAPL", "2023-01-07", 168.0, 172.0, 167.0, None, 1600000),
            ("AAPL", "2023-01-08", 170.0, 168.0, 165.0, 167.0, 1700000),  # High < Low
            ("AAPL", "2023-01-09", 167.0, 175.0, 166.0, 173.0, -100),     # Negative volume
        ]
        
        df = spark.createDataFrame(
            sample_data, 
            ["symbol", "date", "open", "high", "low", "close", "volume"]
        )
        
        # Clean the data
        df_cleaned = clean_stock_data(df)
        
        # Validate the cleaned data
        is_valid = validate_data(df_cleaned)
        
        if is_valid:
            logger.info("Data cleaning and validation successful")
            # In a real implementation, we would write the cleaned data to a destination
            # df_cleaned.write.format("jdbc").option(...).save()
        else:
            logger.warning("Data validation failed after cleaning")
        
        # Show the cleaned data
        logger.info("Cleaned data sample:")
        df_cleaned.show()
        
    except Exception as e:
        logger.error(f"Error in data cleaning: {e}")
    finally:
        spark.stop()
        logger.info("Spark session stopped")

if __name__ == "__main__":
    main()
