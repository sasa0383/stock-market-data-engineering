import yfinance as yf
from config import YAHOO_INTERVALS, TOPIC_TEMPLATE, KAFKA_BROKER
from kafka_producer import send_to_kafka
from datetime import datetime

# 🧠 Main function to handle all intervals for a given symbol
def fetch_and_publish_all_intervals(symbol):
    for label, (interval, period) in YAHOO_INTERVALS.items():

        print(f"📥 Fetching {interval} data for {symbol}...")
        try:
            # 🔁 Download OHLCV data for this symbol & interval
            df = yf.download(symbol, interval=interval, period=period, progress=False)

            if df.empty:
                print(f"⚠️ No data for {symbol} at interval {interval}")
                continue

            # 🧠 Iterate over each row (each timestamped record)
            for ts, row in df.iterrows():
                record = {
                    "symbol": symbol,
                    "interval": interval,
                    "timestamp": str(ts),
                    "open": row["Open"],
                    "high": row["High"],
                    "low": row["Low"],
                    "close": row["Close"],
                    "volume": row["Volume"],
                    "source": "live",
                    "fetched_at": datetime.utcnow().isoformat()
                }

                # 🧪 Define Kafka topic dynamically like "aapl_1m_data"
                topic = TOPIC_TEMPLATE.format(
                    symbol_lower=symbol.lower(),
                    interval=label
                )

                # 📤 Send the message to Kafka
                send_to_kafka(topic, record)

        except Exception as e:
            print(f"❌ Failed to fetch {interval} data for {symbol}: {e}")
