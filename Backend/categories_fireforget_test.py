# send_fire_and_forget.py
import pika, json, os

RABBITMQ_HOST = os.getenv("RABBITMQ_HOST", "localhost")
CATEGORIES_TO_SHAREDALBUM_QUEUE = "categories_to_sharedalbum_queue"

# Sample message simulating Categories microservice
message = {
    "album_id": "korea trip",
    "subcategory_list_album": [
        "Shopping",
        "Food",
    ],  #! Depends on what is in Outsystems DB for 'Korea Trip' shared album subcategoires
    "new_vid_id": "1",
}

connection = pika.BlockingConnection(pika.ConnectionParameters(host=RABBITMQ_HOST))
channel = connection.channel()

# Ensure queue exists (idempotent)
channel.queue_declare(queue=CATEGORIES_TO_SHAREDALBUM_QUEUE, durable=True)

channel.basic_publish(
    exchange="",
    routing_key=CATEGORIES_TO_SHAREDALBUM_QUEUE,
    body=json.dumps(message),
    properties=pika.BasicProperties(delivery_mode=2),  # Make message persistent
)

print(f"Sent fire-and-forget message: {message}")
connection.close()
