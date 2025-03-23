"""
Data Cleaner for Stock Market Data Engineering Project
Provides functions for cleaning and preprocessing stock market data.
"""

import logging
from pyspark.sql import DataFrame
from pyspark.sql.functions import col, when, avg, stddev, lit, isnan, isnull
from pyspark.sql.window import Window
import pyspark.sql.functions as F

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('data-cleaner')

def remove_outliers(df, column_name, threshold=3.0):
    """
    Remove outliers from the dataframe using z-score method.
    
    Args:
        df: Spark DataFrame
        column_name: Column to check for outliers
        threshold: Z-score threshold (default: 3.0)
        
    Returns:
        DataFrame with outliers removed
    """
    logger.info(f"Removing outliers from column {column_name} with threshold {threshold}")
    
    # Calculate mean and standard deviation
    stats = df.select(
        avg(col(column_name)).alias("mean"),
        stddev(col(column_name)).alias("stddev")
    ).collect()[0]
    
    mean_val = stats["mean"]
    stddev_val = stats["stddev"]
    
    # Skip outlier removal if stddev is 0 or null
    if stddev_val is None or stddev_val == 0:
        logger.warning(f"Standard deviation for {column_name} is zero or null. Skipping outlier removal.")
        return df
    
    # Calculate z-score and filter outliers
    logger.info(f"Mean: {mean_val}, StdDev: {stddev_val}")
    
    return df.filter(
        (col(column_name).isNull()) |
        (F.abs((col(column_name) - lit(mean_val)) / lit(stddev_val)) <= lit(threshold))
    )

def fill_missing_values(df):
    """
    Fill missing values in the dataframe.
    
    Args:
        df: Spark DataFrame
        
    Returns:
        DataFrame with missing values filled
    """
    logger.info("Filling missing values")
    
    # Get list of numeric columns
    numeric_columns = [field.name for field in df.schema.fields 
                      if field.dataType.simpleString() in ('double', 'float', 'int', 'long')]
    
    # Get list of string columns
    string_columns = [field.name for field in df.schema.fields 
                     if field.dataType.simpleString() == 'string']
    
    # Fill numeric columns with mean of the column
    for column in numeric_columns:
        # Check if column has null values
        if df.filter(col(column).isNull() | isnan(col(column))).count() > 0:
            # Calculate mean excluding null values
            mean_val = df.select(avg(col(column))).collect()[0][0]
            
            if mean_val is not None:
                logger.info(f"Filling missing values in {column} with mean: {mean_val}")
                df = df.withColumn(
                    column,
                    when(col(column).isNull() | isnan(col(column)), mean_val).otherwise(col(column))
                )
            else:
                logger.warning(f"Cannot calculate mean for {column}, all values are null")
    
    # Fill string columns with most frequent value
    for column in string_columns:
        # Check if column has null values
        if df.filter(col(column).isNull()).count() > 0:
            # Find most frequent value
            most_frequent = df.groupBy(column).count().orderBy(col("count").desc()).first()
            
            if most_frequent and most_frequent[0] is not None:
                most_frequent_val = most_frequent[0]
                logger.info(f"Filling missing values in {column} with most frequent value: {most_frequent_val}")
                df = df.withColumn(
                    column,
                    when(col(column).isNull(), most_frequent_val).otherwise(col(column))
                )
            else:
                logger.warning(f"Cannot find most frequent value for {column}")
    
    return df

def normalize_column(df, column_name):
    """
    Normalize a numeric column to range [0, 1].
    
    Args:
        df: Spark DataFrame
        column_name: Column to normalize
        
    Returns:
        DataFrame with normalized column added
    """
    logger.info(f"Normalizing column {column_name}")
    
    # Calculate min and max
    min_max = df.select(
        F.min(col(column_name)).alias("min"),
        F.max(col(column_name)).alias("max")
    ).collect()[0]
    
    min_val = min_max["min"]
    max_val = min_max["max"]
    
    # Skip normalization if min equals max
    if min_val == max_val:
        logger.warning(f"Min equals max for {column_name}. Skipping normalization.")
        return df.withColumn(f"{column_name}_normalized", lit(0.5))
    
    # Add normalized column
    return df.withColumn(
        f"{column_name}_normalized",
        (col(column_name) - lit(min_val)) / (lit(max_val) - lit(min_val))
    )

def handle_duplicate_timestamps(df, timestamp_col="timestamp", value_col="price"):
    """
    Handle duplicate timestamps by averaging values.
    
    Args:
        df: Spark DataFrame
        timestamp_col: Timestamp column name
        value_col: Value column to average
        
    Returns:
        DataFrame with duplicate timestamps resolved
    """
    logger.info(f"Handling duplicate timestamps in {timestamp_col}")
    
    # Group by timestamp and symbol, then average the values
    return df.groupBy(timestamp_col, "symbol").agg(
        avg(value_col).alias(value_col),
        F.sum("volume").alias("volume"),
        F.count("*").alias("count")
    )
