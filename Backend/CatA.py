from flask import Flask, request, jsonify
import requests
import pika
import json

app = Flask(__name__)

# === OutSystems endpoint ===
OUTSYSTEMS_BASE_URL = "https://personal-e6asw36f.outsystemscloud.com/VideoCategories/rest/RetrieveVideoCategories"

HEADERS = {
    "Content-Type": "application/json",
}

# === RabbitMQ setup ===
amqp_host = "localhost"
amqp_port = 5672
exchange_name = "video_processing_topic"
exchange_type = "topic"

# Establish connection
connection = pika.BlockingConnection(
    pika.ConnectionParameters(host=amqp_host, port=amqp_port, heartbeat=300, blocked_connection_timeout=300)
)
channel = connection.channel()

# Declare exchange
channel.exchange_declare(exchange=exchange_name, exchange_type=exchange_type, durable=True)

# === OutSystems interaction ===
def video_exists(video_id, category, email):
    url = f"{OUTSYSTEMS_BASE_URL}/VideoExists"
    payload = {
        "VideoId": video_id,
        "category": category,
        "email": email
    }

    response = requests.post(url, json=payload, headers=HEADERS)

    if response.status_code == 200:
        return response.text.strip().lower() == "true"
    else:
        print("Error checking video existence:", response.status_code)
        print(response.text)
        return False

def insert_video(video_id, category, email):
    url = f"{OUTSYSTEMS_BASE_URL}/InsertPersonal"
    payload = {
        "VideoId": video_id,
        "category": category,
        "email": email
    }

    response = requests.post(url, json=payload, headers=HEADERS)

    if response.status_code == 200:
        print("Video inserted into OutSystems")
    else:
        print("Error inserting video:", response.status_code)
        print(response.text)

def handle_video_post(video_id, email, category=""):
    # Step 1: Check if video exists in OutSystems
    if video_exists(video_id, category, email):
        print("Video already exists in OutSystems. Skipping insert.")
        return

    # Step 2: Publish to RabbitMQ to be processed
    message = {
        "video_id": video_id,
        "email": email
    }

    channel.basic_publish(
        exchange=exchange_name,
        routing_key="video.to_process",
        body=json.dumps(message),
        properties=pika.BasicProperties(delivery_mode=2)
    )
    print("Sent video to video processor via RabbitMQ")

# === Route to handle POST from gateway ===
@app.route('/post_video', methods=['POST'])
def post_video():
    data = request.get_json()
    print("Received JSON data:", data)

    video_id = data.get("video") or data.get("video_id")
    email = data.get("email")
    category = data.get("categories", "")

    if not video_id or not email:
        return jsonify({
            "error": "Missing video or email",
            "data_received": data
        }), 400

    try:
        handle_video_post(video_id, email, category)
        return jsonify({"message": "Video processed"}), 200
    except Exception as e:
        print("Error in handle_video_post:", str(e))
        return jsonify({"error": "Internal Server Error", "details": str(e)}), 500

# === Start Flask App ===
if __name__ == "__main__":
    app.run(host='localhost', port=5001, debug=True)
