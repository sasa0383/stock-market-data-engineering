"""
Aggregation module for Stock Market Data Engineering Project
Provides functions for aggregating and analyzing stock market data.
"""

import logging
from pyspark.sql import DataFrame
from pyspark.sql.functions import col, lag, lead, when, lit, datediff, date_format
from pyspark.sql.window import Window
import pyspark.sql.functions as F

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('aggregation')

def calculate_moving_averages(df, price_col="avg_price", date_col="date", symbol_col="symbol"):
    """
    Calculate moving averages (5-day, 20-day, 50-day) for stock prices.
    
    Args:
        df: Spark DataFrame with daily stock data
        price_col: Column name for price
        date_col: Column name for date
        symbol_col: Column name for stock symbol
        
    Returns:
        DataFrame with moving averages added
    """
    logger.info("Calculating moving averages")
    
    # Define window specifications for different moving averages
    window_5d = Window.partitionBy(symbol_col).orderBy(date_col).rowsBetween(-4, 0)
    window_20d = Window.partitionBy(symbol_col).orderBy(date_col).rowsBetween(-19, 0)
    window_50d = Window.partitionBy(symbol_col).orderBy(date_col).rowsBetween(-49, 0)
    
    # Calculate moving averages
    return df.withColumn("ma_5d", F.avg(col(price_col)).over(window_5d)) \
             .withColumn("ma_20d", F.avg(col(price_col)).over(window_20d)) \
             .withColumn("ma_50d", F.avg(col(price_col)).over(window_50d))

def detect_trends(df, price_col="avg_price", date_col="date", symbol_col="symbol"):
    """
    Detect price trends (uptrend, downtrend, sideways) based on price movements.
    
    Args:
        df: Spark DataFrame with daily stock data
        price_col: Column name for price
        date_col: Column name for date
        symbol_col: Column name for stock symbol
        
    Returns:
        DataFrame with trend indicators added
    """
    logger.info("Detecting price trends")
    
    # Define window for previous day
    window_prev = Window.partitionBy(symbol_col).orderBy(date_col)
    
    # Add previous day's price
    df_with_prev = df.withColumn("prev_price", lag(col(price_col), 1).over(window_prev))
    
    # Calculate daily price change and percentage change
    df_with_change = df_with_prev.withColumn(
        "price_change", col(price_col) - col("prev_price")
    ).withColumn(
        "price_change_pct", 
        when(col("prev_price").isNotNull() & (col("prev_price") != 0),
             (col(price_col) - col("prev_price")) / col("prev_price") * 100
        ).otherwise(lit(0))
    )
    
    # Determine trend based on moving averages (if available)
    if "ma_5d" in df.columns and "ma_20d" in df.columns:
        df_with_trend = df_with_change.withColumn(
            "trend",
            when(col("ma_5d") > col("ma_20d"), "uptrend")
            .when(col("ma_5d") < col("ma_20d"), "downtrend")
            .otherwise("sideways")
        )
    else:
        # Determine trend based on price change if moving averages not available
        df_with_trend = df_with_change.withColumn(
            "trend",
            when(col("price_change") > 0, "uptrend")
            .when(col("price_change") < 0, "downtrend")
            .otherwise("sideways")
        )
    
    return df_with_trend

def calculate_volatility(df, price_col="avg_price", date_col="date", symbol_col="symbol", window_size=10):
    """
    Calculate price volatility over a specified window.
    
    Args:
        df: Spark DataFrame with daily stock data
        price_col: Column name for price
        date_col: Column name for date
        symbol_col: Column name for stock symbol
        window_size: Number of days to calculate volatility over
        
    Returns:
        DataFrame with volatility metrics added
    """
    logger.info(f"Calculating {window_size}-day volatility")
    
    # Define window for volatility calculation
    volatility_window = Window.partitionBy(symbol_col).orderBy(date_col).rowsBetween(-(window_size-1), 0)
    
    # Calculate standard deviation of prices over the window
    return df.withColumn(f"volatility_{window_size}d", F.stddev(col(price_col)).over(volatility_window))

def calculate_relative_strength(df, price_col="avg_price", date_col="date", symbol_col="symbol", market_symbol="SPY"):
    """
    Calculate relative strength compared to market index.
    
    Args:
        df: Spark DataFrame with daily stock data for multiple symbols
        price_col: Column name for price
        date_col: Column name for date
        symbol_col: Column name for stock symbol
        market_symbol: Symbol representing the market index
        
    Returns:
        DataFrame with relative strength metrics added
    """
    logger.info(f"Calculating relative strength against {market_symbol}")
    
    # Get market data
    market_data = df.filter(col(symbol_col) == market_symbol).select(
        col(date_col),
        col(price_col).alias("market_price")
    )
    
    # Join market data with stock data
    df_with_market = df.join(market_data, on=date_col, how="left")
    
    # Calculate relative strength
    return df_with_market.withColumn(
        "relative_strength",
        when(col("market_price").isNotNull() & (col("market_price") != 0),
             col(price_col) / col("market_price")
        ).otherwise(lit(None))
    )

def aggregate_by_sector(df, sector_col="sector", price_col="avg_price", date_col="date"):
    """
    Aggregate stock data by sector.
    
    Args:
        df: Spark DataFrame with stock data including sector information
        sector_col: Column name for sector
        price_col: Column name for price
        date_col: Column name for date
        
    Returns:
        DataFrame with sector-level aggregations
    """
    logger.info("Aggregating data by sector")
    
    # Group by date and sector
    return df.groupBy(date_col, sector_col).agg(
        F.avg(price_col).alias("sector_avg_price"),
        F.max(price_col).alias("sector_max_price"),
        F.min(price_col).alias("sector_min_price"),
        F.sum("volume").alias("sector_total_volume"),
        F.count("*").alias("stock_count")
    )
