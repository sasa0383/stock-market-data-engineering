import pandas as pd
from kafka_producer import send_to_kafka
from config import KAGGLE_CSV_PATH
from datetime import datetime

KAFKA_TOPIC = "kaggle_historical_data"

def push_kaggle_data_to_kafka():
    print(f"📥 Loading historical data from: {KAGGLE_CSV_PATH}")

    try:
        df = pd.read_csv(KAGGLE_CSV_PATH)

        required_columns = {"Name", "date", "open", "high", "low", "close", "volume"}
        if not required_columns.issubset(set(df.columns)):
            raise ValueError(f"Missing one or more required columns: {required_columns}")

        print(f"✅ Loaded {len(df)} rows. Pushing to Kafka...")

        for _, row in df.iterrows():
            record = {
                "symbol": row["Name"],
                "timestamp": row["date"],
                "open": row["open"],
                "high": row["high"],
                "low": row["low"],
                "close": row["close"],
                "volume": row["volume"],
                "interval": "1d",
                "source": "historical",
                "fetched_at": datetime.utcnow().isoformat()
            }

            send_to_kafka(KAFKA_TOPIC, record)

        print("✅ All historical records pushed to Kafka.")

    except Exception as e:
        print(f"❌ Failed to load and send Kaggle data: {e}")
