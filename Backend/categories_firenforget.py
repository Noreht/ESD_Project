#! This below file is just a reference for Varrya to simulate fire n forget testing for step 9
#! Fire and forget dunnid exchange

# send_fire_and_forget.py
import pika, json, os

RABBITMQ_HOST = os.getenv("RABBITMQ_HOST", "localhost")  #! Please dont change

exchange_name = "categories_to_sharedalbum_topic"
CATEGORIES_TO_SHAREDALBUM_QUEUE = (
    "categories_to_sharedalbum_queue"  #! Please dont change
)

# Sample message simulating Categories microservice
message = {
    "album_id": "Korea Trip",
    "subcategory_list_album": [
        "Shopping",
        "Food",
    ],  #! Depends on what is in Outsystems DB for 'Korea Trip' shared album subcategoires
    "new_vid_id": "1",
    "new_vid_category": "Shopping",  #! depends on Video Processing
    "input_person": "chrisposkitt@is214.com",
    "subscriber_list": [
        "wlunlun1212@gmail.com",
        "wluncheng1212@gmail.com",
        "owen.tay.2023@scis.smu.edu.sg",
    ],
}


connection = pika.BlockingConnection(pika.ConnectionParameters(host=RABBITMQ_HOST))
channel = connection.channel()
channel.exchange_declare(exchange=exchange_name, exchange_type="topic", durable=True)

# Ensure queue exists (idempotent)
# channel.queue_declare(queue=CATEGORIES_TO_SHAREDALBUM_QUEUE, durable=True) #! Please dont change

channel.basic_publish(
    exchange="categories_to_sharedalbum_topic",
    routing_key="cat_firenforget",
    body=json.dumps(message),
    properties=pika.BasicProperties(delivery_mode=2),  # Make message persistent
)

print(
    f"\nSent fire-and-forget message via topic exchange to shared_album.py: {message}"
)
connection.close()
