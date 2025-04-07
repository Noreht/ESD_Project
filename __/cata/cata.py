from flask import Flask, request, jsonify
from threading import Thread
import requests
import pika, json, os
from flask_cors import CORS
from dotenv import load_dotenv
import time

app = Flask(__name__)
CORS(app)

# === OutSystems endpoint ===
OUTSYSTEMS_BASE_URL = "https://personal-e6asw36f.outsystemscloud.com/VideoCategories/rest/RetrieveVideoCategories"

HEADERS = {
    "Content-Type": "application/json",
}

load_dotenv()

# === RabbitMQ setup ===

amqp_host = os.getenv("RABBITMQ_HOST", "localhost")  # Default to localhost if not set
amqp_port = int(os.getenv("RABBITMQ_PORT", 5672))
username = os.getenv("RABBITMQ_USER", "myuser")  #! (this may be 'guest')
password = os.getenv("RABBITMQ_PASS", "mypassword")


exchange_name = "video_processing_topic"
exchange_type = "topic"

credentials = pika.PlainCredentials(username, password)

# Establish connection
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

# Declare exchange
channel.exchange_declare(
    exchange=exchange_name, exchange_type=exchange_type, durable=True
)


# === OutSystems interaction ===
def video_exists(video_id, category, email, album_id):
    GATEWAY_URL = os.getenv("GATEWAY_URL", "http://gateway:3000")
    url = f"{GATEWAY_URL}/CheckExists"
    payload = {
        "VideoId": video_id,
        "category": category,
        "email": email,
        "AlbumId": album_id,
    }

    response = requests.post(url, json=payload, headers=HEADERS)

    print(response)

    #! Regardless of whether it is in Outsystems, just send for [Video Processing]
    if response.status_code == 200:
        print("✅ Video Exists... But just send to [Video Processing] ...")
        return response.text.strip().lower() == "true"

    else:
        print("\n ❌ Error checking video existence:", response.status_code)
        print(response.text)
        return False


def insert_video(video_id, category, email):
    url = f"{OUTSYSTEMS_BASE_URL}/InsertPersonal"
    payload = {"VideoId": video_id, "category": category, "email": email}

    response = requests.post(url, json=payload, headers=HEADERS)

    if response.status_code == 200:
        print("Video inserted into OutSystems")
    else:
        print("Error inserting video:", response.status_code)
        print(response.text)


def handle_video_post(video_id, email, category="", album_id="", subscriber_list=[]):
    # Step 1: Check if Outsystems can be reached, if not... fk the insertion
    if video_exists(video_id, category, email, album_id):
        print("Video already exists in OutSystems. Skipping insert.\n")
        return

    #! Scenario 2: This confirm is [Shared Album] send one
    if album_id != "":

        message = {"video_id": video_id, "album_id": album_id, "email": email, "subscriber_list": subscriber_list}

        # ✅ Send AQMP to [Video Processing]
        channel.basic_publish(
            exchange="video_processing_topic",
            routing_key="scenario_2_video_processing_queue",
            body=json.dumps(message),
            properties=pika.BasicProperties(delivery_mode=2),
        )

        print(
            f"🟢 [Event Broker] -> [Me] -> Sent to [Video Processor] for processing ... "
        )

    #! This is Scenario 1
    else:

        # Step 2: Publish to [Video Processing] via RabbitMQ
        message = {"video_id": video_id, "email": email}

        channel.basic_publish(
            exchange=exchange_name,
            routing_key="video.to_process",
            body=json.dumps(message),
            properties=pika.BasicProperties(delivery_mode=2),
        )
        print(
            "🟢 [Scenario 1]: Sent video succesfully to [Video Processor] via RabbitMQ\n"
        )


# TODO: [Gateway] -> [CatA] -> [Video Processing] via handle_video_post() without 'album_id'
@app.route("/post_video", methods=["POST"])
def post_video():
    data = request.get_json()
    print("Received JSON data:", data, "\n")

    video_id = data.get("video") or data.get("video_id")
    email = data.get("email")
    category = data.get("categories", "")

    if not video_id or not email:
        return jsonify({"error": "Missing video or email", "data_received": data}), 400
    print("🔍 Checking video existence in Outsystems ...", video_id, email, category)
    try:
        handle_video_post(video_id, email, category, album_id="")
        return jsonify({"message": "Video processed"}), 200
    except Exception as e:
        print("Error in handle_video_post:", str(e))
        return jsonify({"error": "Internal Server Error", "details": str(e)}), 500


def callback(ch, method, properties, body):
    print(f"🟢 Received message from [SharedAlbum] -> [Event Broker] -> [Me] ...\n")
    print(f"🟢 Received Message Structure: {body}\n")

    #  msg_to_event_broker = {
    #         "video_id": video_id,
    #         "album_id": album_id,
    #         "subscriber_list": new_subscriber_list,  # Gotten from Supabase
    #         "input_person": input_person_email,
    #     }

    try:
        data = json.loads(body)
        video_id = data.get("video_id")
        album_id = data.get("album_id")
        subscriber_list = data.get("subscriber_list")
        email = data.get("email") or data.get("input_person")
        category = data.get("category", "")

        handle_video_post(video_id, email, category, album_id=album_id, subscriber_list=subscriber_list)

    except Exception as e:
        print(f"❌ Error processing SharedAlbum message: {str(e)}")


#! Scenario 2: [CatA] listening to [Shared Album] at [Gateway]
def start_consumer():
    while True:
        try:
            # Re-establish connection
            connection = pika.BlockingConnection(
                pika.ConnectionParameters(
                    host=amqp_host,
                    port=amqp_port,
                    credentials=pika.PlainCredentials(username, password),
                    heartbeat=300,
                    blocked_connection_timeout=300,
                )
            )
            channel = connection.channel()

            # Declare exchange & queue
            exchange_name = "event_broker_exchange"
            queue_name = "sharedalbum_to_catA_queue"
            routing_key = "sharedalbum.process"

            channel.exchange_declare(
                exchange=exchange_name, exchange_type="fanout", durable=True
            )
            channel.queue_declare(queue=queue_name, durable=True)
            channel.queue_bind(exchange=exchange_name, queue=queue_name)

            print(
                f"🟢 [Cat A] is listening to [Shared Album] on queue [{queue_name}] for routing key '{routing_key}'"
            )

            # Start consuming
            channel.basic_consume(
                queue=queue_name, on_message_callback=callback, auto_ack=True
            )
            channel.start_consuming()

        except pika.exceptions.AMQPConnectionError as e:
            print(f"❌ [CatA] RabbitMQ connection error: {e}. Retrying in 5 seconds...")
            time.sleep(5)  # Wait before retrying
        except Exception as e:
            print(f"❌ [CatA] Unexpected error: {e}. Retrying in 5 seconds...")
            time.sleep(5)

# === Start Flask App ===
if __name__ == "__main__":
    # Start RabbitMQ consumer in the background thread
    consumer_thread = Thread(target=start_consumer)
    consumer_thread.daemon = True
    consumer_thread.start()

    # Run Flask in the main thread with debug=True
    app.run(host="0.0.0.0", port=5001, debug=True)
