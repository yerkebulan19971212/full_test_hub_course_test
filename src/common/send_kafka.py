import json
from confluent_kafka import Producer

conf = {
    "bootstrap.servers": "37.140.243.80:9092",  # или IP сервера
    "acks": "all",
    "retries": 1,
}

producer = Producer(conf)


def delivery_report(err, msg):
    if err:
        print(f"❌ Delivery failed: {err}")
    else:
        print(
            f"✅ Delivered to {msg.topic()} [{msg.partition()}]"
        )


def send_to_kafka(topic: str, data: dict):
    producer.produce(
        topic=topic,
        value=json.dumps(data).encode("utf-8"),
        callback=delivery_report,
    )

    producer.poll(1)

#
# if __name__ == "__main__":
#     print("Sending to Kafka")
#
#     send_to_kafka(
#         "Ptopic1",
#         {"question_id": 1, "question": "akdjalskdfjalskdfalskdfj"}
#     )
#
#     producer.flush()
#     print("Message sent")
