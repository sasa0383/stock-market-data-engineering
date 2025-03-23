"""
Producer Service Entry Point
Filters symbols by price and fetches multi-interval stock data from Yahoo Finance
"""
from load_kaggle_data import push_kaggle_data_to_kafka
push_kaggle_data_to_kafka()

from symbol_filter import get_symbols_below_price
from yahoo_finance_api import fetch_and_publish_all_intervals
import logging

# Logging setup
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('producer-service')

def main():
    logger.info("🚀 Starting Producer Service...")

    try:
        # Step 1: Filter symbols based on price
        symbols = get_symbols_below_price()
        logger.info(f"✅ Found {len(symbols)} symbols below price threshold.")

        # Step 2: Fetch data for each symbol and push to Kafka
        for symbol in symbols:
            logger.info(f"🔄 Processing symbol: {symbol}")
            fetch_and_publish_all_intervals(symbol)

        logger.info("✅ All symbols processed. Producer job complete.")

    except Exception as e:
        logger.error(f"❌ Fatal error in producer service: {e}")

if __name__ == "__main__":
    main()
