from confluent_kafka import Consumer, KafkaException
import json
from ETL.load_github import load_data_into_mongodb
import time

def consume_kafka_messages(topic, loader, timeout=600):
    c = Consumer({
        'bootstrap.servers': 'kafka:9092',
        'group.id': 'mygroup',
        'auto.offset.reset': 'earliest'
    })

    c.subscribe([topic])
    start_time = time.time()

    try:
        while True:
            if time.time() - start_time > timeout:
                print("Timeout reached. Stopping the consumer.")
                break

            msg = c.poll(1.0)
            if msg is None:
                continue
            if msg.error():
                if msg.error().code() == KafkaException._PARTITION_EOF:
                    print(f"Reached end of partition: {msg.error()}")
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
        print("Consumer interrupted by user")

    finally:
        c.close()
        print("Consumer closed")
