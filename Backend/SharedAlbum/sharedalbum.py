from flask import Flask, jsonify, request
import requests
from dotenv import load_dotenv
import os,sys, pika, json, threading
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from sharedalbumeventbroker.sharedalbum_eventbroker import publish_to_event_broker

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
RABBITMQ_HOST = os.getenv(
    "RABBITMQ_HOST","rabbitmq"
)  # Default to localhost if not set
port = int(os.getenv("RABBITMQ_PORT", 5672))
username = os.getenv("RABBITMQ_USER", "myuser")  #! (this may be 'guest')
password = os.getenv("RABBITMQ_PASS", "mypassword")


#! Step 8 (Fire and Forget)
def process_message(channel, method, properties, body):
    print(f"\nReceived message from Categories (Step 8): {body}\n")

    # try:
    #     # Parse incoming message from Categories (Fire and Forget)

    #     message = json.loads(body)
    #     album_id = (
    #         "Korea Trip"  #! Hardcoded to be 'korea trip', else: message.get("album_id")
    #     )
    #     subcategory_list_album = message.get(
    #         "subcategory_list_album"
    #     )  #! Name may differ
    #     new_vid_id = message.get("new_vid_id")  #! New Video added

    #     new_vid_category = message.get("new_vid_category")

    #     if not album_id or not new_vid_id:
    #         print("Invalid message: Missing album_id or new_vid_id")
    #         return

    #     # Fetch album details from Supabase ({album_id, album_name, subscriber_list})
    #     endpoint = f"{SUPABASE_URL}/rest/v1/{TABLE_NAME}"
    #     headers = {
    #         "apikey": SUPABASE_ANON_KEY,
    #         "Authorization": f"Bearer {SUPABASE_ANON_KEY}",
    #     }
    #     response = requests.get(
    #         endpoint, headers=headers, params={"album_id": f"eq.{album_id}"}
    #     )

    #     if response.status_code != 200:
    #         print(f"Failed to fetch album {album_id} from Supabase")
    #         return

    #     album_data = response.json()

    #     if not album_data:
    #         print(f"Album {album_id} not found in Supabase")
    #         return

    #     album = album_data[0]  #! Returns 1st column

    #     subscriber_list_bad = album.get("subscriber_list")[0]
    #     new_subscriber_list = subscriber_list_bad.split(",")

    #     # Construct message for Notifications
    #     notification_message = {
    #         "vid_id": new_vid_id,
    #         "new_vid_subcategory": new_vid_category,
    #         "shared_album_name": album.get(
    #             "album_name"
    #         ),  # from Supabase -> 'korea trip' duh
    #         "subcategory_list_of_album": subcategory_list_album,  #! From Categories (May need handling to put in a Python List) [from Outsystems DB]
    #         "subscriber_list": new_subscriber_list,  # Text Arr (Supabase dtype -> Python List)
    #     }
    #     SHARED_ALBUM_QUEUE = "shared_album_queue"  # listen to shared_album
    #     SHARED_ALBUM_EXCHANGE = "shared_album_exchange"  # sent by shared_album (step 9)

    #     # Send to Notifications queue
    #     channel.basic_publish(
    #         exchange=SHARED_ALBUM_EXCHANGE,
    #         routing_key=SHARED_ALBUM_QUEUE,
    #         body=json.dumps(notification_message),
    #         properties=pika.BasicProperties(delivery_mode=2),  # Persistent
    #     )

    #     print("Message sent to Notifications [Completed]\n")
    #     print(f"Message Content:{notification_message}\n")

    # except Exception as e:
    #     print(f"Error processing message: {str(e)}")


CATEGORIES_TO_SHAREDALBUM_QUEUE = "categories_to_sharedalbum_queue"
exchange_name = "categories_to_sharedalbum_topic"
queue_name = "categories_to_sharedalbum_queue"
routing_key = "cat_firenforget"


#! RabbitMQ
def start_consumer():
    # Connect to RabbitMQ
   
    RABBITMQ_USER = os.getenv("RABBITMQ_USER", "myuser")
    RABBITMQ_PASS = os.getenv("RABBITMQ_PASS", "mypassword")

    credentials = pika.PlainCredentials(RABBITMQ_USER, RABBITMQ_PASS)
    parameters = pika.ConnectionParameters(host=RABBITMQ_HOST, credentials=credentials)
    connection = pika.BlockingConnection(parameters)
    channel = connection.channel()
   

    # Declare exchange
    channel.exchange_declare(
        exchange=exchange_name, exchange_type="topic", durable=True
    )

    # Declare queues
    channel.queue_declare(queue=CATEGORIES_TO_SHAREDALBUM_QUEUE, durable=True)

    # Bind queue to the exchange with the same routing key
    channel.queue_bind(
        exchange=exchange_name, queue=queue_name, routing_key=routing_key
    )

    # Start consuming with your handler for Step 9
    channel.basic_consume(
        queue=queue_name,
        on_message_callback=process_message,
        auto_ack=True
    )
    
    print("Waiting for messages from Categories...")
    channel.start_consuming()


# TODO2: Returns msg to UI "Wait User!" upon a POST request to Shared Album microservice ✅
@app.route("/shared-album/add", methods=["POST"])
@cross_origin()  # 👈 Add this decorator
def add_video_to_shared_album():
    data = request.get_json()  # Get the JSON from the UI
    print(data)
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

        # TODO3: Send AQMP to Event Broker (Scenario 2) - Step 3
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

    app.run(debug=True, port=5100)
