#! This below file is just a reference for Varrya to simulate fire n forget testing for step 9
#! Fire and forget dunnid exchange

# send_fire_and_forget.py
import pika, json, os

RABBITMQ_HOST = os.getenv("RABBITMQ_HOST", "localhost") #! Please dont change
CATEGORIES_TO_SHAREDALBUM_QUEUE = "categories_to_sharedalbum_queue" #! Please dont change

# Sample message simulating Categories microservice
message = {
    "album_id": "korea trip",
    "subcategory_list_album": [
        "Shopping",
        "Food",
    ],  #! Depends on what is in Outsystems DB for 'Korea Trip' shared album subcategoires
    "new_vid_id": "1",
    "new_vid_category": "Shopping",  #! depends on Video Processing
}

connection = pika.BlockingConnection(pika.ConnectionParameters(host=RABBITMQ_HOST))
channel = connection.channel()

# Ensure queue exists (idempotent)
channel.queue_declare(queue=CATEGORIES_TO_SHAREDALBUM_QUEUE, durable=True) #! Please dont change

channel.basic_publish(
    exchange="",
    routing_key=CATEGORIES_TO_SHAREDALBUM_QUEUE,
    body=json.dumps(message),
    properties=pika.BasicProperties(delivery_mode=2),  # Make message persistent
)

print(f"\nSent fire-and-forget message: {message}")
connection.close()
