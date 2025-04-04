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

def insert_into_outsystems(video_id, category, email):
    url = f"http://localhost:3000/InsertProcessedVideo"
    payload = {
        "VideoId": video_id,
        "category": category,
        "email": email
    }

    headers = {
        "Content-Type": "application/json"
    }

    print(f"[CatB] Sending to OutSystems → {json.dumps(payload)}")

    try:
        response = requests.post(url, json=payload, headers=headers)
        print(f"[CatB] OutSystems responded with status {response.status_code}")
        print("Response body:", response.text)

        if response.status_code == 200:
            print(f"[CatB] Inserted: {video_id} → {category} for {email}")
        else:
            print(f"[CatB] Failed to insert. Status: {response.status_code}")

    except Exception as e:
        print("[CatB] Error calling OutSystems:", str(e))

# === Callback for processing messages ===
def callback(ch, method, properties, body):
    try:
        print("[CatB] Received message from RabbitMQ:", body)
        data = json.loads(body)
        video_id = data.get("video_id")
        category = data.get("categories", "Uncategorized")
        email = data.get("email")

        if not video_id or not email:
            print("[CatB] Missing video_id or email in message:", data)
            ch.basic_nack(delivery_tag=method.delivery_tag)
            return

        insert_into_outsystems(video_id, category, email)
        ch.basic_ack(delivery_tag=method.delivery_tag)

    except Exception as e:
        print("[CatB] Error processing message:", str(e))
        ch.basic_nack(delivery_tag=method.delivery_tag)

# === Start listening ===
def start_consuming():
    channel.queue_bind(queue="Processed_Videos", exchange="video_processing_topic", routing_key="video.processed")
    channel.basic_consume(queue="Processed_Videos", on_message_callback=callback, auto_ack=False)
    print(f"[CatB] Listening on queue '{queue_name}'...")
    channel.start_consuming()

if __name__ == "__main__":
    print("[CatB] Starting CatB consumer...")
    start_consuming()
