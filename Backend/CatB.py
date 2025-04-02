import json
import pika
import requests

# === RabbitMQ setup ===
amqp_host = "localhost"
amqp_port = 5672
exchange_name = "video_processing_topic"
exchange_type = "topic"
queue_name = "Processed_Videos"
routing_key = "video.processed"

# Establish connection
connection = pika.BlockingConnection(
    pika.ConnectionParameters(host=amqp_host, port=amqp_port, heartbeat=300, blocked_connection_timeout=300)
)
channel = connection.channel()

# Declare exchange and queue
channel.exchange_declare(exchange=exchange_name, exchange_type=exchange_type, durable=True)
channel.queue_declare(queue=queue_name, durable=True)
channel.queue_bind(exchange=exchange_name, queue=queue_name, routing_key=routing_key)

# === OutSystems endpoint ===
OUTSYSTEMS_BASE_URL = "https://personal-e6asw36f.outsystemscloud.com/VideoCategories/rest/RetrieveVideoCategories"

def insert_into_outsystems(video_id, category, email="zuwei@example.com"):
    url = f"{OUTSYSTEMS_BASE_URL}/InsertPersonal"
    payload = {
        "VideoId": video_id,
        "category": category,
        "email": email
    }

    headers = {
        "Content-Type": "application/json"
    }

    try:
        response = requests.post(url, json=payload, headers=headers)
        if response.status_code == 200:
            print(f"Inserted: {video_id} → {category}")
        else:
            print(f"Failed to insert. Status: {response.status_code}")
            print("Response:", response.text)
    except Exception as e:
        print("Error calling OutSystems:", str(e))

# === Callback for processing messages ===
def callback(ch, method, properties, body):
    try:
        print("Received message from RabbitMQ")
        data = json.loads(body)
        video_id = data.get("video")
        category = data.get("categories", "Uncategorized")

        if video_id:
            insert_into_outsystems(video_id, category)
        else:
            print("No video_id in message:", data)

        ch.basic_ack(delivery_tag=method.delivery_tag)

    except Exception as e:
        print("Error processing message:", str(e))
        ch.basic_nack(delivery_tag=method.delivery_tag)

# === Start listening ===
def start_consuming():
    channel.basic_consume(queue=queue_name, on_message_callback=callback)
    print(f"Listening on queue '{queue_name}'...")
    channel.start_consuming()

if __name__ == "__main__":
    print("Starting CatB consumer...")
    start_consuming()
