from flask import Flask, jsonify, request
import requests
from dotenv import load_dotenv
import os, pika, json

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


# TODO1 : Connect to Supabase (Shared Album DB) - Add video_id and Read

app = Flask(__name__)

load_dotenv()  # Load environment variables from .env file


SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_ANON_KEY = os.getenv("SUPABASE_KEY")


# TODO2: Return Text Array (Subcategories) to UI ('Korea Trip' shared album displays 'Food', 'Shopping'....)
# use 'http://127.0.0.1:5001/get_data' (Returns Subcategory List to UI)
@app.route("/get_data", methods=["GET"])
def get_data():
    # Use the correct table endpoint
    TABLE_NAME = "sharedalbum"  # Replace with your actual table name
    endpoint = f"{SUPABASE_URL}/rest/v1/{TABLE_NAME}"  # entire table

    headers = {
        "apikey": SUPABASE_ANON_KEY,
        "Authorization": f"Bearer {SUPABASE_ANON_KEY}",
    }

    album_id = "1"  #! Theron UI press Album_ID

    response = requests.get(
        endpoint,
        headers=headers,
        params={
            "select": "subcategory_list",
            "album_id": f"eq.{album_id}",  # Filter by album_id
        },
    )

    if response.status_code == 200:
        return jsonify(response.json()), 200

    else:
        return (
            jsonify({"error": "Failed to fetch data from Supabase"}),
            response.status_code,
        )


# TODO2: Exposes POST endpoint URL (Adds video_id ) x Supabase


# TODO3: Publish message to RabbitMQ (Publish-Subscribe)
RABBITMQ_HOST = "localhost"  #! TF
FANOUT_EXCHANGE = "shared_album_fanout"


def publish_to_rabbitmq(vidid, subscriber_list, shared_album_name):
    """Publish message to RabbitMQ fanout exchange."""
    try:
        # Establish connection
        connection = pika.BlockingConnection(pika.ConnectionParameters(RABBITMQ_HOST))
        channel = connection.channel()

        # Declare fanout exchange (durable to survive broker restarts)
        channel.exchange_declare(
            exchange=FANOUT_EXCHANGE, exchange_type="fanout", durable=True
        )

        # Prepare message
        message = {
            "vid_id": vidid,
            "subscriber_list": subscriber_list,
            "shared_album_name": shared_album_name,
        }

        # Publish message
        channel.basic_publish(
            exchange=FANOUT_EXCHANGE,
            routing_key="",  # Fanout ignores routing key
            body=json.dumps(message),
            properties=pika.BasicProperties(
                delivery_mode=2,  # Persistent message
            ),
        )
        connection.close()
        return True
    except Exception as e:
        print(f"Error publishing message: {e}")
        return False


# New POST endpoint to add video and publish message to RabbitMQ Broker
#! Receive album details from frontend
@app.route("/add_video", methods=["POST"])
def add_video():
    data = request.get_json()
    vidid = data.get("vidid")

    #! Get shared_album_id from Frontend (Reads from Shared Album DB -> Needs album's subscriber_list and shared_album name)
    subscriber_list = data.get("subscriber_list")
    shared_album_name = data.get("shared_album_name")

    # Publish message to RabbitMQ
    if publish_to_rabbitmq(vidid, subscriber_list, shared_album_name):
        return (
            jsonify(
                {"status": "success", "message": "Video added and message published"}
            ),
            201,
        )
    else:
        return jsonify({"status": "error", "message": "Failed to publish message"}), 500


if __name__ == "__main__":
    app.run(debug=True, port=5001)
