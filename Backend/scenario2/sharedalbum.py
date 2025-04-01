from flask import Flask, jsonify, request
import requests
from dotenv import load_dotenv
import os, pika, json, threading
from sharedalbum_eventbroker import (
    publish_to_event_broker,
)  # 👈 import your broker logic


# Define shared_album dictionary
categories = {
    "Korea Travel": [
        "Shopping",
        "Food",
        "Landmarks",
        "Photo Worthy",
        "Hotel",
        "Music Bank",
        "Itinerary",
        "Instagrammable",
    ]
}


app = Flask(__name__)

# TODO1: Steps 8 and 9 (Listens for Fire n Forget from Categories, Reads from Supabase & Sends AMQP to Notifications)
import pika
import requests
import json

# Supabase Configuration
load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_ANON_KEY = os.getenv("SUPABASE_KEY")
TABLE_NAME = "sharedalbum"

# RabbitMQ Configuration
RABBITMQ_HOST = "localhost"
CATEGORIES_TO_SHAREDALBUM_QUEUE = "categories_to_sharedalbum_queue"
NOTIFICATIONS_QUEUE = "notifications_queue"


#! Step 8 (Fire and Forget)
def process_message(channel, method, properties, body):
    print(f"\nReceived message from Categories (Step 8): {body}\n")

    try:
        # Parse incoming message from Categories (Fire and Forget)

        message = json.loads(body)
        album_id = (
            "korea trip"  #! Hardcoded to be 'korea trip', else: message.get("album_id")
        )
        subcategory_list_album = message.get(
            "subcategory_list_album"
        )  #! Name may differ
        new_vid_id = message.get("new_vid_id")  #! New Video added

        new_vid_category = message.get("new_vid_category")

        if not album_id or not new_vid_id:
            print("Invalid message: Missing album_id or new_vid_id")
            return

        # Fetch album details from Supabase ({album_id, album_name, subscriber_list})
        endpoint = f"{SUPABASE_URL}/rest/v1/{TABLE_NAME}"
        headers = {
            "apikey": SUPABASE_ANON_KEY,
            "Authorization": f"Bearer {SUPABASE_ANON_KEY}",
        }
        response = requests.get(
            endpoint, headers=headers, params={"album_id": f"eq.{album_id}"}
        )

        if response.status_code != 200:
            print(f"Failed to fetch album {album_id} from Supabase")
            return

        album_data = response.json()

        if not album_data:
            print(f"Album {album_id} not found in Supabase")
            return

        album = album_data[0]  #! Returns 1st column

        subscriber_list_bad = album.get("subscriber_list")[0]
        new_subscriber_list = subscriber_list_bad.split(",")

        # Construct message for Notifications
        notification_message = {
            "vid_id": new_vid_id,
            "new_vid_subcategory": new_vid_category,
            "shared_album_name": album.get(
                "album_name"
            ),  # from Supabase -> 'korea trip' duh
            "subcategory_list_of_album": subcategory_list_album,  #! From Categories (May need handling to put in a Python List) [from Outsystems DB]
            "subscriber_list": new_subscriber_list,  # Text Arr (Supabase dtype -> Python List)
        }
        SHARED_ALBUM_QUEUE = "shared_album_queue"  # listen to shared_album
        SHARED_ALBUM_EXCHANGE = "shared_album_exchange"  # sent by shared_album (step 9)

        # Send to Notifications queue
        channel.basic_publish(
            exchange=SHARED_ALBUM_EXCHANGE,
            routing_key=SHARED_ALBUM_QUEUE,
            body=json.dumps(notification_message),
            properties=pika.BasicProperties(delivery_mode=2),  # Persistent
        )

        print("Message sent to Notifications [Completed]\n")
        print(f"Message Content:{notification_message}\n")

    except Exception as e:
        print(f"Error processing message: {str(e)}")


#! RabbitMQ
def start_consumer():
    # Connect to RabbitMQ
    connection = pika.BlockingConnection(pika.ConnectionParameters(host=RABBITMQ_HOST))
    channel = connection.channel()

    # Declare queues
    channel.queue_declare(queue=CATEGORIES_TO_SHAREDALBUM_QUEUE, durable=True)
    channel.queue_declare(queue=NOTIFICATIONS_QUEUE, durable=True)

    # Start consuming
    channel.basic_consume(
        queue=CATEGORIES_TO_SHAREDALBUM_QUEUE,
        on_message_callback=process_message,
        auto_ack=True,
    )
    print("Waiting for messages from Categories...")
    channel.start_consuming()


# TODO2: Returns msg to UI "Wait User!" upon a POST request to Shared Album microservice
@app.route("/shared-album/add", methods=["POST"])
def add_video_to_shared_album():
    data = request.get_json()  # Get the JSON from the UI
    if not data:
        return jsonify({"error": "No JSON received"}), 400

    # Extract expected fields from JSON
    video_id = data.get("video_id")
    album_id = data.get("album_id")  #! Prolly hard-coded to 'korea trip'
    input_person_email = data.get(
        "input_person_email"
    )  #! Prolly need input field / hardcoded on UI layer

    # Fetch album details from Supabase ({album_id, album_name, subscriber_list})
    endpoint = f"{SUPABASE_URL}/rest/v1/{TABLE_NAME}"

    headers = {
        "apikey": SUPABASE_ANON_KEY,
        "Authorization": f"Bearer {SUPABASE_ANON_KEY}",
    }
    response = requests.get(
        endpoint, headers=headers, params={"album_id": f"eq.{album_id}"}
    )

    if response.status_code != 200:
        print(f"Failed to fetch album {album_id} from Supabase")
        return

    album_data = response.json()

    if not album_data:
        print(f"Album {album_id} not found in Supabase")
        return

    album = album_data[0]  #! Returns 1st column

    subscriber_list_bad = album.get("subscriber_list")[0]
    new_subscriber_list = subscriber_list_bad.split(",")

    # TODO3: Send AQMP to Event Broker (Scenario 2) - Step 3
    # {video_id, album_name, subscriber_list, category, input_email}
    msg_to_event_broker = {
        "video_id": video_id,
        "album_id": album_id,
        "subscriber_list": new_subscriber_list,  # Gotten from Supabase
        "input_person": input_person_email,
    }

    publish_to_event_broker(msg_to_event_broker)

    # Respond to UI after sending message to Event Broker
    return (
        jsonify(
            {
                "message": f"Ok, my love 💋! Please patiently wait for autocategorisation within {album_id}"
            }
        ),
        200,
    )


# Run the gawddamn app
if __name__ == "__main__":
    #! Start consumer in a background thread -> To do Consuming from Queue and Run app at the same time!
    consumer_thread = threading.Thread(target=start_consumer, daemon=True)
    consumer_thread.start()

    app.run(debug=True, port=5100)


