from flask import Flask, jsonify, request
import requests
from dotenv import load_dotenv
import os, pika, json, threading

import sys
import os


from SharedAlbumEventBroker.sharedalbum_eventbroker import publish_to_event_broker


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


from flask_cors import CORS, cross_origin  # 👈 Make sure this is imported

app = Flask(__name__)
CORS(app)  # 👈 Allow all origins (*) for all routes

# TODO1: Steps 8 and 9 (Listens for Fire n Forget from Categories, Reads from Supabase & Sends AMQP to Notifications)
import pika
import requests
import json

# Supabase Configuration
load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_ANON_KEY = os.getenv("SUPABASE_KEY")
TABLE_NAME = "sharedalbum"

# RabbitMQ Configuration (Get from Environment)
aqmp_host = os.getenv("RABBITMQ_HOST", "localhost")  # Default to localhost if not set
port = int(os.getenv("RABBITMQ_PORT", 5672))
username = os.getenv("RABBITMQ_USER", "myuser")  #! (this may be 'guest')
password = os.getenv("RABBITMQ_PASS", "mypassword")


#! Step 8 (Fire and Forget)
def process_message(channel, method, properties, body):
    print(f"\nReceived message from Categories (Step 8): {body}\n")

    try:
        # Parse the message
        message = json.loads(body)
        album_id = message.get("album_id", "")

        if album_id:
            print(
                f"🟢 [SharedAlbum] Sending album_id to [Gateway-Frontend]: {album_id}"
            )

            # Send album_id to frontend
            frontend_url = "http://gateway:3000/NotifyFrontend"
            payload = {"album_id": album_id}
            headers = {"Content-Type": "application/json"}

            try:
                response = requests.post(frontend_url, json=payload, headers=headers)
                print(
                    f"🟢 [SharedAlbum] Frontend responded with status {response.status_code}"
                )
                print("Response body:", response.text)

            except Exception as e:
                print(f"❌ [SharedAlbum] Error sending album_id to frontend: {str(e)}")

    except Exception as e:
        print(f"❌ [SharedAlbum] Error processing message from CatB: {str(e)}")


CATEGORIES_TO_SHAREDALBUM_QUEUE = "categories_to_sharedalbum_queue"
exchange_name = "categories_to_sharedalbum_topic"
queue_name = "categories_to_sharedalbum_queue"
routing_key = "cat_firenforget"


#! RabbitMQ - For [CatB]
def start_consumer():

    catb_to_sharedalbum_exchange = "catb_to_sharedalbum_exchange"
    catb_to_sharedalbum_queue = "catb_to_sharedalbum_queue"

    # Connect to RabbitMQ
    aqmp_host = os.getenv(
        "RABBITMQ_HOST", "localhost"
    )  # Default to localhost if not set
    username = os.getenv("RABBITMQ_USER", "myuser")  #! (this may be 'guest')
    password = os.getenv("RABBITMQ_PASS", "mypassword")
    port = int(os.getenv("RABBITMQ_PORT", 5672))

    if not aqmp_host:
        raise ValueError("RABBITMQ_HOST environment variable is not set.")

    credentials = pika.PlainCredentials(username, password)

    connection = pika.BlockingConnection(
        pika.ConnectionParameters(host=aqmp_host, credentials=credentials, port=port)
    )

    channel = connection.channel()

    # Declare exchange and queue
    channel.exchange_declare(
        exchange=catb_to_sharedalbum_exchange, exchange_type="fanout", durable=True
    )
    channel.queue_declare(queue=catb_to_sharedalbum_queue, durable=True)
    channel.queue_bind(
        exchange=catb_to_sharedalbum_exchange, queue=catb_to_sharedalbum_queue
    )

    # Start consuming with your handler for Step 9
    channel.basic_consume(
        queue=catb_to_sharedalbum_queue,
        on_message_callback=process_message,
        auto_ack=True,
    )

    print("🟢 Waiting for messages from [CatB]...\n")
    channel.start_consuming()


# TODO2: Publish POST from [Frontend] to [Event Broker] -> [CatA]
@app.route("/shared-album/add", methods=["POST"])
@cross_origin()  # 👈 Add this decorator
def add_video_to_shared_album():
    data = request.get_json()  # Get the JSON from the UI

    print(f"🟢 Received Message from [Frontend] [Save to Shared Album] ...\n")

    print(f"🟢 Message Structure: {data}\n")

    if not data:
        return jsonify({"error": "No JSON received"}), 400

    # Extract expected fields from JSON
    video_id = data.get("video_id")
    album_id = data.get("album_id")  #! Prolly hard-coded to 'korea trip'
    input_person_email = data.get(
        "input_person_email"
    )  #! Prolly need input field / hardcoded on UI layer

    # JSON Fields Debugging
    required_fields = ["video_id", "album_id", "input_person_email"]
    if not all(field in data for field in required_fields):
        print("Missing required fields")
        return jsonify({"error": "Missing required fields"}), 400

    # Fetch album details from Supabase ({album_id, album_name, subscriber_list})

    try:
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

        # TODO3: Send AQMP to [Event Broker]
        # {video_id, album_name, subscriber_list, category, input_email}
        msg_to_event_broker = {
            "video_id": video_id,
            "album_id": album_id,
            "subscriber_list": new_subscriber_list,  # Gotten from Supabase
            "input_person": input_person_email,
        }

        try:
            publish_to_event_broker(msg_to_event_broker)

        except Exception as e:
            print(f"Failed to publish to event broker: {str(e)}")
            return jsonify({"error": "Event broker communication failed"}), 500

        return (
            jsonify(
                {
                    "message": f"Ok, my love 💋! Please patiently wait for autocategorisation within {album_id}"
                }
            ),
            200,
        )

    except Exception as e:
        print(f"Unexpected error: {str(e)}")
        return jsonify({"error": "Internal server error"}), 500


# Run the gawddamn app
if __name__ == "__main__":
    #! Start consumer in a background thread -> To do Consuming from Queue and Run app at the same time!
    consumer_thread = threading.Thread(target=start_consumer, daemon=True)
    consumer_thread.start()

    app.run(host="0.0.0.0", port=5100, debug=True)
