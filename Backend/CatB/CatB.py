import json
import pika
import requests
import os
from threading import Thread


# === RabbitMQ setup ===

amqp_host = os.getenv("RABBITMQ_HOST", "localhost")  # Default to localhost if not set
amqp_port = int(os.getenv("RABBITMQ_PORT", 5672))
username = os.getenv("RABBITMQ_USER", "myuser")  #! (this may be 'guest')
password = os.getenv("RABBITMQ_PASS", "mypassword")


exchange_name = "video_processing_topic"
exchange_type = "topic"

# Scenario 1 Queue
queue_name = "Processed_Videos"
routing_key = "video.processed"  #! Scenario 1: Receive from [VidProc]

# Scenario 2 Queue
scenario_2_queue = "scenario_2_video_processing_queue"
scenario_2_routing_key = "scenario_2.processed"  #! Scenario 2 routing key


# Establish connection
credentials = pika.PlainCredentials("myuser", "mypassword")

connection = pika.BlockingConnection(
    pika.ConnectionParameters(
        host=amqp_host,
        port=amqp_port,
        heartbeat=300,
        blocked_connection_timeout=300,
        credentials=credentials,
    )
)
channel = connection.channel()

# Declare Exchange
channel.exchange_declare(
    exchange=exchange_name, exchange_type=exchange_type, durable=True
)

# Declare Queue (Scenario 1)
channel.queue_declare(queue=queue_name, durable=True)

# Declare Queue (Scenario 2)
channel.queue_declare(queue=scenario_2_queue)


# === OutSystems endpoint ===
OUTSYSTEMS_BASE_URL = "https://personal-e6asw36f.outsystemscloud.com/VideoCategories/rest/RetrieveVideoCategories"


def insert_into_outsystems(video_id, category, email, album_id="", subscriber_list=[]):
    url = f"http://gateway:3000/InsertProcessedVideo"
    payload = {
        "VideoId": video_id,
        "category": category,
        "email": email,
        "albumid": album_id,
    }

    headers = {"Content-Type": "application/json"}

    print(f"\n🟢 [CatB] Sending to OutSystems → {json.dumps(payload)}\n")

    try:
        response = requests.post(url, json=payload, headers=headers)
        print(f"🟢 [CatB] OutSystems responded with status {response.status_code}\n")
        print("Response body:", response.text, "\n")

        if response.status_code == 200:
            print(f"🟢 [CatB] Inserted: {video_id} → {category} for {email}")
            # Fire-and-forget to sharedalbum if album_id exists
            if album_id:
                fire_and_forget_to_sharedalbum(
                    video_id, category, email, album_id, subscriber_list=subscriber_list
                )
        else:
            print(f"[CatB] Failed to insert. Status: {response.status_code}")

    except Exception as e:
        print("[CatB] Error calling OutSystems:", str(e))


def fire_and_forget_to_sharedalbum(
    video_id, category, email, album_id, subscriber_list=[]
):

    catb_to_sharedalbum_exchange = "catb_to_sharedalbum_exchange"

    # Construct the message
    message = {
        "video_id": video_id,
        "category": category,
        "email": email,
        "album_id": album_id,
        "subscriber_list": subscriber_list,
    }

    print(
        f"\n🟢 [CatB] Sending fire-and-forget to [Shared Album] → {json.dumps(message)}\n"
    )

    try:
        # Declare RabbitMQ connection and channel
        credentials = pika.PlainCredentials("myuser", "mypassword")
        connection = pika.BlockingConnection(
            pika.ConnectionParameters(host="rabbitmq", credentials=credentials)
        )
        channel = connection.channel()

         # Declare exchange
        channel.exchange_declare(
            exchange=catb_to_sharedalbum_exchange, exchange_type="fanout", durable=True
        )

        # Publish the message
        channel.basic_publish(
            exchange=catb_to_sharedalbum_exchange,
            routing_key="",
            body=json.dumps(message),
            properties=pika.BasicProperties(delivery_mode=2),  # Persistent message
        )
        print(f"🟢 [CatB] Fire-and-forget message sent to [Shared Album]: {message}\n")

        connection.close()
        
    except Exception as e:
        print(f"❌ [CatB] Error sending fire-and-forget to sharedalbum: {str(e)}")


# === Callback for processing messages ===
def callback(ch, method, properties, body):
    try:
        # ✅ Distinguish between Scenario 1 and Scenario 2
        if method.routing_key == "video.processed":
            print(
                f"🟢 [CatB] Scenario 1: Received [Processed Video] for [Save Video]  ... {body}"
            )

        elif method.routing_key == "scenario_2.processed":
            print(
                f"🟢 [CatB] Scenario 2: Received [Processed Video] for [Shared Album] ... {body}"
            )

        data = json.loads(body)
        video_id = data.get("video_id")
        category = data.get("categories", "Uncategorized")
        email = data.get("email") or data.get("email_id")
        album_id = data.get("album_id", "")
        subscriber_list = data.get("subscriber_list", [])

        if not video_id or not email:
            print("[CatB] Missing video_id or email in message:", data)
            ch.basic_nack(delivery_tag=method.delivery_tag)
            return

        insert_into_outsystems(
            video_id,
            category,
            email,
            album_id=album_id,
            subscriber_list=subscriber_list,
        )

        #! Send {album_id} to Frontend so Frontend read {album_id} f
        #! from Outsystems and get all subcategories for that shared_album
        #! Theron: Inset Here

        ch.basic_ack(delivery_tag=method.delivery_tag)

    except Exception as e:
        print("❌ [CatB] Error processing message:", str(e))
        ch.basic_ack(delivery_tag=method.delivery_tag)


# === Start listening ===
def start_consuming():

    # Bind Scenario 1
    channel.queue_bind(
        exchange=exchange_name, queue=queue_name, routing_key=routing_key
    )

    # Bind Scenario 2 (This is to populate into Outsystems with 'album_id' and 'category')
    channel.queue_bind(
        exchange=exchange_name,
        queue=scenario_2_queue,
        routing_key=scenario_2_routing_key,
    )

    channel.basic_consume(
        queue=queue_name, on_message_callback=callback, auto_ack=False
    )

    print(f"[CatB] Listening on queue '{queue_name}' for Scenario 1...")

    # Consume from Scenario 2 queue
    channel.basic_consume(
        queue=scenario_2_queue, on_message_callback=callback, auto_ack=False
    )

    print(f"[CatB] Listening on queue '{scenario_2_queue}' for Scenario 2...")

    channel.start_consuming()


if __name__ == "__main__":
    print("🟢 [CatB] Starting CatB consumer...")

    # 🧵 Start RabbitMQ consumer in a separate thread
    consumer_thread = Thread(target=start_consuming, daemon=True)
    consumer_thread.start()

    # 🛑 Do NOT run Flask here if you're not using Flask in CatB
    # Just block main thread so it doesn’t exit:
    consumer_thread.join()
