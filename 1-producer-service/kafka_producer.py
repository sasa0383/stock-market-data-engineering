from kafka import KafkaProducer
import json
from config import KAFKA_BROKER

# 🔧 Step 1: Create a Kafka producer with JSON serialization
producer = KafkaProducer(
    bootstrap_servers=KAFKA_BROKER,
    value_serializer=lambda v: json.dumps(v).encode("utf-8")
)

# 📤 Step 2: Function to send a message to Kafka
def send_to_kafka(topic, message):
    try:
        producer.send(topic, value=message)
        print(f"✅ Sent message to topic: {topic}")
    except Exception as e:
        print(f"❌ Failed to send message to {topic}: {e}")
