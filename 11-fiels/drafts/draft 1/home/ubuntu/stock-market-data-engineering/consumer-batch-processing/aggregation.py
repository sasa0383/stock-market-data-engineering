#!/usr/bin/env python3
"""
Aggregation module for Stock Market Data Engineering Project
Performs various aggregations on stock data for batch processing
"""

import logging
from pyspark.sql import SparkSession
from pyspark.sql.functions import col, avg, max, min, sum, count, stddev, expr
from pyspark.sql.window import Window
import pyspark.sql.functions as F

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def create_spark_session():
    """Create and return a Spark session"""
    return (SparkSession.builder
            .appName("StockDataAggregation")
            .getOrCreate())

def calculate_volatility(df):
    """Calculate volatility metrics for stocks"""
    logger.info("Calculating volatility metrics")
    
    # Calculate daily price range percentage
    df_with_range = df.withColumn(
        "daily_range_pct", 
        (col("high") - col("low")) / col("low") * 100
    )
    
    # Calculate volatility (standard deviation of daily returns)
    df_with_returns = df_with_range.withColumn(
        "daily_return", 
        (col("close") - col("open")) / col("open") * 100
    )
    
    # Group by symbol and calculate volatility metrics
    volatility_df = df_with_returns.groupBy("symbol").agg(
        stddev("daily_return").alias("return_volatility"),
        avg("daily_range_pct").alias("avg_daily_range_pct"),
        max("daily_range_pct").alias("max_daily_range_pct")
    )
    
    return volatility_df

def calculate_trend_indicators(df):
    """Calculate trend indicators for stocks"""
    logger.info("Calculating trend indicators")
    
    # Define window specifications for different periods
    window_7d = Window.partitionBy("symbol").orderBy("date").rowsBetween(-7, 0)
    window_30d = Window.partitionBy("symbol").orderBy("date").rowsBetween(-30, 0)
    window_90d = Window.partitionBy("symbol").orderBy("date").rowsBetween(-90, 0)
    
    # Calculate moving averages
    df_with_ma = df.withColumn("ma_7d", avg("close").over(window_7d)) \
                   .withColumn("ma_30d", avg("close").over(window_30d)) \
                   .withColumn("ma_90d", avg("close").over(window_90d))
    
    # Calculate trend indicators
    trend_df = df_with_ma.withColumn(
        "trend_short", 
        when(col("ma_7d") > col("ma_30d"), 1).otherwise(-1)
    ).withColumn(
        "trend_long", 
        when(col("ma_30d") > col("ma_90d"), 1).otherwise(-1)
    )
    
    # Get the most recent trend indicators for each symbol
    window_latest = Window.partitionBy("symbol").orderBy(col("date").desc())
    latest_trends = trend_df.withColumn("row_num", F.row_number().over(window_latest)) \
                           .filter(col("row_num") == 1) \
                           .select("symbol", "trend_short", "trend_long", "date")
    
    return latest_trends

def calculate_volume_profile(df):
    """Calculate volume profile metrics for stocks"""
    logger.info("Calculating volume profile metrics")
    
    # Calculate average daily volume
    avg_volume = df.groupBy("symbol").agg(
        avg("volume").alias("avg_daily_volume"),
        stddev("volume").alias("volume_volatility"),
        max("volume").alias("max_volume")
    )
    
    # Calculate relative volume (compared to 30-day average)
    window_30d = Window.partitionBy("symbol").orderBy("date").rowsBetween(-30, -1)
    df_with_rel_vol = df.withColumn(
        "avg_30d_volume", 
        avg("volume").over(window_30d)
    ).withColumn(
        "relative_volume", 
        col("volume") / col("avg_30d_volume")
    )
    
    # Get the most recent relative volume for each symbol
    window_latest = Window.partitionBy("symbol").orderBy(col("date").desc())
    latest_rel_vol = df_with_rel_vol.withColumn("row_num", F.row_number().over(window_latest)) \
                                   .filter(col("row_num") == 1) \
                                   .select("symbol", "relative_volume", "date")
    
    # Join the metrics
    volume_profile = avg_volume.join(latest_rel_vol, "symbol")
    
    return volume_profile

def calculate_sector_performance(df, sector_mapping):
    """Calculate sector performance metrics"""
    logger.info("Calculating sector performance metrics")
    
    # Join with sector mapping
    df_with_sector = df.join(sector_mapping, "symbol")
    
    # Calculate sector average returns
    sector_returns = df_with_sector.groupBy("sector").agg(
        avg(col("close") / col("open") - 1).alias("avg_daily_return"),
        count("symbol").alias("num_stocks")
    )
    
    return sector_returns

def main():
    """Main function to perform stock data aggregation"""
    logger.info("Starting Stock Data Aggregation")
    
    # Create Spark session
    spark = create_spark_session()
    
    try:
        # In a real implementation, we would read from a source like:
        # df = spark.read.format("jdbc").option(...).load()
        
        # For demonstration, we'll create a sample DataFrame
        logger.info("Creating sample DataFrame for demonstration")
        sample_data = [
            ("AAPL", "2023-01-01", 150.0, 155.0, 148.0, 152.0, 1000000),
            ("AAPL", "2023-01-02", 152.0, 158.0, 151.0, 157.0, 1200000),
            ("AAPL", "2023-01-03", 157.0, 160.0, 155.0, 159.0, 1100000),
            ("MSFT", "2023-01-01", 250.0, 255.0, 248.0, 252.0, 800000),
            ("MSFT", "2023-01-02", 252.0, 258.0, 251.0, 257.0, 900000),
            ("MSFT", "2023-01-03", 257.0, 260.0, 255.0, 259.0, 850000),
        ]
        
        df = spark.createDataFrame(
            sample_data, 
            ["symbol", "date", "open", "high", "low", "close", "volume"]
        )
        
        # Sample sector mapping
        sector_data = [
            ("AAPL", "Technology"),
            ("MSFT", "Technology"),
            ("GOOGL", "Technology"),
            ("JPM", "Financial"),
            ("BAC", "Financial"),
        ]
        
        sector_mapping = spark.createDataFrame(
            sector_data,
            ["symbol", "sector"]
        )
        
        # Calculate various aggregations
        volatility = calculate_volatility(df)
        trends = calculate_trend_indicators(df)
        volume_profile = calculate_volume_profile(df)
        sector_performance = calculate_sector_performance(df, sector_mapping)
        
        # Show results
        logger.info("Volatility metrics:")
        volatility.show()
        
        logger.info("Trend indicators:")
        trends.show()
        
        logger.info("Volume profile:")
        volume_profile.show()
        
        logger.info("Sector performance:")
        sector_performance.show()
        
        # In a real implementation, we would write the results to a destination
        # volatility.write.format("jdbc").option(...).save()
        
    except Exception as e:
        logger.error(f"Error in data aggregation: {e}")
    finally:
        spark.stop()
        logger.info("Spark session stopped")

if __name__ == "__main__":
    main()
