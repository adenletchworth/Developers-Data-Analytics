from confluent_kafka import Consumer, KafkaException
import json
from ETL.load_reddit import load_data_into_mongodb

def consume_kafka_messages(topic, loader):
    c = Consumer({
        'bootstrap.servers': 'kafka:9092',
        'group.id': 'mygroup',
        'auto.offset.reset': 'earliest'
    })

    c.subscribe([topic])

    try:
        while True:
            msg = c.poll(1.0)
            if msg is None:
                continue
            if msg.error():
                if msg.error().code() == KafkaException._PARTITION_EOF:
                    continue
                else:
                    print(f"Kafka error: {msg.error()}")
                    break

            # Decode JSON message
            try:
                data = json.loads(msg.value().decode('utf-8'))
                print(f"Consumed message: {data}")
            except json.JSONDecodeError as e:
                print(f"JSON decode error: {e}")
                continue

            if isinstance(data, dict):
                data = [data]

            loader(data)

    except KeyboardInterrupt:
        pass

    finally:
        c.close()

if __name__ == "__main__":
    consume_kafka_messages('reddit_topic', load_data_into_mongodb)
